use axum::{
    extract::{
        ws::{Message, WebSocket},
        State, WebSocketUpgrade,
    },
    http::{HeaderValue, Response},
    response::IntoResponse,
    routing::get,
    Form, Router,
};
use futures::{stream::SplitSink, SinkExt, StreamExt};
use reqwest::{header, StatusCode};
use std::sync::Arc;
use tokio::{
    fs,
    io::{AsyncWriteExt, Sink},
    net::TcpListener,
    process::Command,
    sync::{Mutex, RwLock},
};
use tracing::{error, Level};
use uuid::Uuid;

const TEMPLATE: &str = include_str!("template.tex");

macro_rules! ise {
    () => {
        return Response::builder()
            .status(StatusCode::INTERNAL_SERVER_ERROR)
            .body("Internal Server Error".to_string())
            .unwrap()
    };
}

#[derive(Clone)]
struct ConnectionManager {
    connections: Arc<Mutex<Vec<SplitSink<WebSocket, Message>>>>,
}

impl ConnectionManager {
    pub fn new() -> Self {
        Self {
            connections: Arc::new(Mutex::new(vec![])),
        }
    }

    pub async fn add_sink(&self, sink: SplitSink<WebSocket, Message>) {
        self.connections.lock().await.push(sink);
    }

    pub async fn broardcast_str(&self, message: &str) {
        futures::stream::iter(self.connections.lock().await.iter_mut())
            .for_each_concurrent(None, move |item| {
                let message = message.to_string();
                async move {
                    if let Err(ex) = item.send(Message::Text(message)).await {
                        error!("Could not send message to client {ex}");
                    }
                }
            })
            .await;
    }
}

#[derive(serde::Deserialize)]
struct DeaththreatRequest {
    title: String,
    first_name: String,
    last_name: String,
    address_line_1: String,
    address_line_2: String,
    suburb: String,
    city: String,
    postcode: String,
    description: String,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_file(true)
        .with_line_number(true)
        .with_max_level(Level::DEBUG)
        .init();

    let router = Router::new()
        .route("/submit", get(submit))
        .route("/jobs", get(jobs))
        .with_state(ConnectionManager::new());

    let listener = TcpListener::bind("0.0.0.0:8000")
        .await
        .expect("Could not bind to 0.0.0.0:8000");

    axum::serve(listener, router.into_make_service())
        .await
        .expect("Could not start axum server");
}

async fn jobs(State(mgr): State<ConnectionManager>, ws: WebSocketUpgrade) -> impl IntoResponse {
    ws.on_upgrade(|ws| async move {
        let (sink, _) = ws.split();
        mgr.add_sink(sink).await;
    })
}

async fn submit(
    State(mgr): State<ConnectionManager>,
    Form(DeaththreatRequest {
        title,
        first_name,
        last_name,
        address_line_1,
        address_line_2,
        suburb,
        city,
        postcode,
        description,
    }): Form<DeaththreatRequest>,
) -> Response<String> {
    let mut latex = TEMPLATE.replace("%FONT%", "Un_funny Death Threat");

    let mut document = format!(
        "\\noindent {title} {first_name} {last_name} \\\\
{address_line_1} \\\\
"
    );

    if !address_line_2.is_empty() {
        document += address_line_2.as_str();
        document += "\\\\\n";
    }

    document += format!(
        "{suburb} \\\\
{city} {postcode} \\\\
\\newline
{description}"
    )
    .as_str();

    let file_id = Uuid::new_v4().to_string();

    let client = reqwest::Client::new();

    match client
        .get("http://srv-captain--autothreat-svg-map:8000")
        .query(&[(
            "q",
            format!("{address_line_1} {address_line_2} + {suburb} + {city} + {postcode}"),
        )])
        .send()
        .await
    {
        Ok(request) if request.status() == StatusCode::OK => {
            if let Ok(svg) = request.text().await {
                latex = latex.replace("%SVG%", format!("\\begin{{filecontents*}}[overwrite]{{map-{file_id}.svg}}\n{svg}\n\\end{{filecontents*}}").as_str());
                document += format!(
                    "\\\\
\\begin{{center}}
    \\includesvg[width=10cm]{{map-{file_id}}}\n
\\end{{center}} \\\\
"
                )
                .as_str();
            } else {
                error!("The map api returned a response that could not be decoded as a svg");
            }
        }
        _ => {
            error!("Could not generate a map SVG");
        }
    }

    latex = latex.replace("%DOC%", document.as_str());

    let tex_file = format!("/tmp/deaththreat-{file_id}.tex");
    let pdf_file = format!("/tmp/deaththreat-{file_id}.pdf");
    let svg_file = format!("/tmp/deaththreat-{file_id}.svg");

    if let Err(ex) = fs::write(tex_file.as_str(), latex.as_str()).await {
        error!("Could not write tex file {ex}");
        ise!();
    }

    let latex_command = match Command::new("/usr/bin/xelatex")
        .args(&[
            "-interaction=nonstopmode",
            "-enable-write18",
            tex_file.as_str(),
        ])
        .current_dir("/tmp")
        .kill_on_drop(true)
        .spawn()
    {
        Ok(child) => child,
        Err(ex) => {
            error!("Could not spawn xelatex {ex}");
            ise!()
        }
    };

    match latex_command.wait_with_output().await {
        Ok(val) if val.status.success() => {}
        Err(ex) => {
            error!("Could not wait for latex compile command to finnish {ex}");
            ise!();
        }

        _ => {}
    }

    let inkscape_command = match Command::new("/usr/bin/inkscape")
        .args(&[
            "--export-text-to-path",
            format!("--export-plain-svg={svg_file}").as_str(),
            pdf_file.as_str(),
        ])
        .current_dir("/tmp")
        .kill_on_drop(true)
        .spawn()
    {
        Ok(child) => child,
        Err(ex) => {
            error!("Could not spawn inkscape: {ex}");
            ise!();
        }
    };

    match inkscape_command.wait_with_output().await {
        Ok(val) if !val.status.success() => {
            error!("inkscape exited with status {}", val.status);
            error!("STDERR");
            let _ = tokio::io::stderr().write_all(&val.stderr).await;
            error!("STDOUT");
            let _ = tokio::io::stderr().write_all(&val.stdout).await;
            ise!();
        }
        Err(ex) => {
            error!("Could not wait for inkscape command to finnish {ex}");
            ise!();
        }

        _ => {}
    }

    let content = match tokio::fs::read_to_string(svg_file).await {
        Ok(val) => val,
        Err(ex) => {
            error!("Could not read svg {ex}");
            ise!();
        }
    };

    mgr.broardcast_str(content.as_str()).await;

    Response::builder()
        .header(
            header::CONTENT_TYPE,
            HeaderValue::from_static("image/svg+xml"),
        )
        .body(content)
        .unwrap()
}
