<script lang="ts">
	import { PUBLIC_FORM_ACTION } from '$env/static/public';
</script>

<div class="flex w-full justify-center py-5">
	<form
		action={PUBLIC_FORM_ACTION}
		method="get"
		class="grid w-3/4 gap-x-10 gap-y-5 lg:grid-cols-[1fr,3fr,3fr]"
	>
		<label class="input input-bordered flex items-center gap-2">
			Recipetiant Title
			<input type="text" class="grow" placeholder="Mr" name="title" />
		</label>

		<label class="input input-bordered flex items-center gap-2">
			Recipetiant First Name
			<input type="text" class="grow" placeholder="John" name="first_name" />
		</label>

		<label class="input input-bordered flex items-center gap-2">
			Recipetiant Last Name
			<input type="text" class="grow" placeholder="Doe" name="last_name" />
		</label>

		<label class="input input-bordered flex items-center gap-2 lg:col-span-3">
			Address Line 1
			<input type="text" class="grow" placeholder="123 Some Road" name="address_line_1" />
		</label>

		<label class="input input-bordered flex items-center gap-2 lg:col-span-3">
			Address Line 2
			<input type="text" class="grow" placeholder="123 Some Road" name="address_line_2" />
			<span class="badge badge-info">Optional</span>
		</label>

		<label class="input input-bordered flex items-center gap-2 lg:col-span-3">
			Suburb
			<input type="text" class="grow" placeholder="Somewhere" name="suburb" />
		</label>

		<label class="input input-bordered flex items-center gap-2 lg:col-span-2">
			City
			<input type="text" class="grow" placeholder="Some city" name="city" />
		</label>
		<label class="input input-bordered flex items-center gap-2">
			Postcode
			<input type="text" class="grow" placeholder="0123" name="postcode" />
		</label>

		<label class="flex flex-col gap-2 lg:col-span-3">
			A description of the threat
			<textarea
				class="textarea textarea-bordered"
				placeholder="I really hate this person"
				name="description"
			></textarea>
		</label>

		<input
			type="submit"
			value="Send"
			class="btn btn-primary w-fit justify-self-center lg:col-span-3"
		/>
	</form>
</div>
