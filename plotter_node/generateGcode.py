from typing import Tuple
import gcodeplot.gcodeplot as glinkplot
import gcodeplot.gcodeplotutils.sendgcode
import xml.etree.ElementTree as ET
import gcodeplot.gcodeplotutils.anneal as anneal

import config.config as ender_config 

def callGCodePlot(data: str) -> Tuple[str, glinkplot.Plotter]:


    final_gcode_out = ""

    tolerance = 0.05
    doDedup = True
    sendPort = None
    sendSpeed = 115200
    hpglLength = 279.4
    scalingMode = glinkplot.SCALE_NONE
    shader = glinkplot.Shader()
    align = [glinkplot.ALIGN_NONE, glinkplot.ALIGN_NONE]
    plotter = glinkplot.Plotter(initCode=";\n", xyMin=ender_config.xyMin, xyMax=ender_config.xyMax, drawSpeed=ender_config.drawSpeed, moveSpeed=ender_config.moveSpeed, zSpeed=ender_config.zSpeed, workZ=ender_config.workZ, liftDeltaZ=ender_config.liftDeltaZ, safeDeltaZ=ender_config.safeDeltaZ, endCode=";\n")
    hpglOut = False
    strokeAll = False
    extractColor = None
    gcodePause = "@pause"
    optimizationTime = 30
    dpi = (1016., 1016.)
    pens = {1:glinkplot.Pen('1 (0.,0.) black default')}
    doDump = False
    penFilename = None
    pauseAtStart = False
    sortPaths = False
    svgSimulation = False
    toolOffset = 0.
    overcut = 0.
    toolMode = "custom"
    booleanExtractColor = False
    quiet = False
    comment = ";"
    sendAndSave = False
    directionAngle = None

    def maybeNone(a):
        return None if a=='none' else a

    if doDump:
        print('no-allow-repeats' if doDedup else 'allow-repeats')

        print('gcode-pause=' + gcodePause)

        if penFilename is not None:
            print('pens=' + penFilename)

        if scalingMode == glinkplot.SCALE_NONE:
            print('scale=none')
        elif scalingMode == glinkplot.SCALE_DOWN_ONLY:
            print('scale=down')
        else:
            print('scale=fit')

        if align[0] == glinkplot.ALIGN_LEFT:
            print('align-x=left')
        elif align[0] == glinkplot.ALIGN_CENTER:
            print('align-x=center')
        elif align[0] == glinkplot.ALIGN_RIGHT:
            print('align-x=right')
        else:
            print('align-x=none')

        if align[1] == glinkplot.ALIGN_BOTTOM:
            print('align-y=bottom')
        elif align[1] == glinkplot.ALIGN_CENTER:
            print('align-y=center')
        elif align[1] == glinkplot.ALIGN_TOP:
            print('align-y=top')
        else:
            print('align-y=none')

        print('tolerance=' + str(tolerance))

        if sendPort is not None:
            print('send=' + str(sendPort))
        else:
            print('no-send')

        print('send-speed=' + str(sendSpeed))
        print('area=%g,%g,%g,%g' % tuple(list(plotter.xyMin)+list(plotter.xyMax)))
        print('input-dpi=%g,%g' % tuple(dpi))
        print('safe-delta-z=%g' % (plotter.safeDeltaZ))
        print('lift-delta-z=%g' % (plotter.liftDeltaZ))
        print('work-z=%g' % (plotter.workZ))
        print('pen-down-speed=%g' % (plotter.drawSpeed))
        print('pen-up-speed=%g' % (plotter.moveSpeed))
        print('z-speed=%g' % (plotter.zSpeed))
        print('hpgl-out' if hpglOut else 'no-hpgl-out')
        print('shading-threshold=%g' % (shader.unshadedThreshold))
        print('shading-lightest=%g' % (shader.lightestSpacing))
        print('shading-darkest=%g' % (shader.darkestSpacing))
        print('shading-angle=%g' % (shader.angle))
        print('shading-crosshatch' if shader.crossHatch else 'no-shading-crosshatch')
        print('stroke-all' if strokeAll else 'no-stroke-all')
        print('optimization-time=%g' % (optimizationTime))
        print('sort' if sortPaths else 'no-sort')
        print('pause-at-start' if pauseAtStart else 'no-pause-at-start')
        print('extract-color=all' if extractColor is None else 'extract-color=rgb(%.3f,%.3f,%.3f)' % tuple(extractColor))
        print('tool-offset=%.3f' % toolOffset)
        print('overcut=%.3f' % overcut)
        print('simulation' if svgSimulation else 'no-simulation')
        print('direction=' + ('none' if directionAngle is None else '%.3f'%directionAngle))
        print('lift-command=' + ('none' if plotter.liftCommand is None else plotter.liftCommand))
        print('down-command=' + ('none' if plotter.downCommand is None else plotter.downCommand))
        print('init-code=' + ('none' if plotter.initCode is None else plotter.initCode))
        print('end-code=' + ('none' if plotter.endCode is None else plotter.endCode))
        print('comment-delimiters=' + ('none' if plotter.comment is None else plotter.comment))


    shader.unshadedThreshold = 0

    if toolMode == 'cut':
        shader.unshadedThreshold = 0
        optimizationTime = 0
        sortPaths = True
        directionAngle = None
    elif toolMode == 'draw':
        toolOffset = 0.
        sortPaths = False
        
    plotter.updateVariables()


        
    if sendPort is not None:
        gcodeplot.gcodeplotutils.sendgcode.sendGcode(port=sendPort, speed=sendSpeed, commands=glinkplot.gcodeHeader(plotter) + [gcodePause], gcodePause=gcodePause, variables=plotter.variables, formulas=plotter.formulas)


    svgTree = None

    try:
        svgTree = glinkplot.ET.fromstring(data)
        if not 'svg' in svgTree.tag:
            svgTree = None
    except:
        svgTree = None

    if svgTree is None and 'PD' not in data and 'PU' not in data:
        print("Unrecognized file.\n")
        exit(1)

    shader.setDrawingDirectionAngle(directionAngle)
    if svgTree is not None:
        penData = glinkplot.parseSVG(svgTree, tolerance=tolerance, shader=shader, strokeAll=strokeAll, pens=pens, extractColor=extractColor)
    else:
        penData =glinkplot. parseHPGL(data, dpi=dpi)
    penData = glinkplot.removePenBob(penData)

    if doDedup:
        penData = glinkplot.dedup(penData)

    if sortPaths:
        for pen in penData:
            penData[pen] = glinkplot.safeSorted(penData[pen], comparison=glinkplot.comparePaths)
        penData = glinkplot.removePenBob(penData)

    if optimizationTime > 0. and directionAngle is None:
        for pen in penData:
            penData[pen] = anneal.optimize(penData[pen], timeout=optimizationTime/2., quiet=quiet)
        penData = glinkplot.removePenBob(penData)

    if toolOffset > 0. or overcut > 0.:
        if scalingMode != glinkplot.SCALE_NONE:
            print("Scaling with tool-offset > 0 will produce unpredictable results.\n")
        op = glinkplot.OffsetProcessor(toolOffset=toolOffset, overcut=overcut, tolerance=tolerance)
        for pen in penData:
            penData[pen] = op.processPath(penData[pen])

    if directionAngle is not None:
        for pen in penData:
            penData[pen] = glinkplot.directionalize(penData[pen], directionAngle)
        penData = glinkplot.removePenBob(penData)

    if len(penData) > 1:
        print("Uses the following pens:\n")
        for pen in sorted(penData):
            print(glinkplot.describePen(pens, pen)+"\n")

    if hpglOut and not svgSimulation:
        g = glinkplot.emitHPGL(penData, pens=pens)
    else:
        g = glinkplot.emitGcode(penData, align=align, scalingMode=scalingMode, tolerance=tolerance,
                plotter=plotter, gcodePause=gcodePause, pens=pens, pauseAtStart=pauseAtStart, simulation=svgSimulation)

    if g:

        if hpglOut:
            print(g)
        else:
            final_gcode_out = ('\n'.join(glinkplot.fixComments(plotter, g, comment=plotter.comment)))
                
        return (final_gcode_out, plotter)
    else:
        print("No output generated.\n")
        return ("", plotter)
