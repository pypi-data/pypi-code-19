import anvil.server
from anvil import *

#!defFunction(anvil.users,_)!2: "Get the row from the users table that corresponds to the current logged-in user" ["get_user"]
def get_user():
	return anvil.server.call("anvil.private.users.get_current_user")

#!defFunction(anvil.users,_)!2: "Forget the current logged-in user" ["logout"]
def logout():
	anvil.server.call("anvil.private.users.logout")

_client_config = {
	'use_google': True,
	'use_raven': False,
	'use_email': True,
	'confirm_email': True,
}

def set_client_config(x):
	global _client_config
	_client_config = x


#!defClass(anvil.users,UserExists)!:
class UserExists(anvil.server.AnvilWrappedError):
	pass


#!defClass(anvil.users,AuthenticationFailed)!:
class AuthenticationFailed(anvil.server.AnvilWrappedError):
	pass


#!defClass(anvil.users,EmailNotConfirmed)!:
class EmailNotConfirmed(AuthenticationFailed):
	pass


#!defClass(anvil.users,AccountIsNotEnabled)!:
class AccountIsNotEnabled(AuthenticationFailed):
	pass


anvil.server._register_exception_type("anvil.users.UserExists", UserExists)
anvil.server._register_exception_type("anvil.users.AuthenticationFailed", AuthenticationFailed)
anvil.server._register_exception_type("anvil.users.EmailNotConfirmed", EmailNotConfirmed)
anvil.server._register_exception_type("anvil.users.AccountIsNotEnabled", AccountIsNotEnabled)

#!defFunction(anvil.users,_,email,password)!2: "Log in with the specified email address and password. Returns None if authentication failed." ["login_with_email"]
def login_with_email(email, password):
	return anvil.server.call("anvil.private.users.login_with_email", email, password)

#!defFunction(anvil.users,_,email,password)!2: "Sign up for a new account with the specified email address and password. Raises anvil.users.UserExists if an account is already registered with this email address." ["signup_with_email"]
def signup_with_email(email, password):
	return anvil.server.call("anvil.private.users.signup_with_email", email, password)

#!defFunction(anvil.users,_,email_address)!2: "Send a password-reset email to the specified user" ["send_password_reset_email"]
def send_password_reset_email(email):
	anvil.server.call("anvil.private.users.send_password_reset_email", email)

if is_server_side():

	#!defFunction(anvil.users,_,user_row)!2: "Set the specified user object (a row from a Data Table) as the current logged-in user. It must be a row from the users table." ["force_login"]
	def force_login(user):
		anvil.server.call("anvil.private.users.force_login", user)

	def _fail(fname):
		def f(*args, **kwargs):
			raise Exception("You can't use " + fname + "() on the server (do it in form code instead)")
		return f

	for n in ["login_with_google", "signup_with_google", "login_with_facebook", "signup_with_facebook", "login_with_raven", "signup_with_raven", "login_with_form", "signup_with_form"]:
		globals()[n] = _fail(n)

else:

	def force_login(user):
		raise Exception("You can only use force_login() in server modules")

	#!defFunction(anvil.users,!)!2: "Log in with a Google account. Prompts the user to authenticate with Google, then logs in with their Google email address (if that user exists). Returns None if the login was cancelled or we have no record of this user." ["login_with_google"]
	def login_with_google(additional_scopes):
		if not _client_config.get("use_google"):
			raise Exception("Google login is not enabled")

		import google.auth
		if google.auth.login(additional_scopes):
			return anvil.server.call("anvil.private.users.login_with_google")

	#!defFunction(anvil.users,!)!2: "Sign up for a new account with the email address associated with the user's Google account. Prompts the user to authenticate with Google, then registers a new user with that email address. Raises anvil.users.UserExists if this email address is already registered; returns new user or None if cancelled." ["signup_with_google"]
	def signup_with_google(additional_scopes):
		if not _client_config.get("use_google"):
			raise Exception("Google signup is not enabled")

		if not _client_config.get("allow_signup"):
			raise Exception("New user signup is not enabled")

		import google.auth
		if google.auth.login():
			return anvil.server.call("anvil.private.users.signup_with_google")

	#!defFunction(anvil.users,!)!2: "Log in with a Facebook account. Prompts the user to authenticate with Facebook, then logs in with their Facebook email address (if that user exists). Returns None if the login was cancelled or we have no record of this user." ["login_with_facebook"]
	def login_with_facebook(additional_scopes):
		if not _client_config.get("use_facebook"):
			raise Exception("Facebook login is not enabled")

		import facebook.auth
		if facebook.auth.login(additional_scopes):
			return anvil.server.call("anvil.private.users.login_with_facebook")

	#!defFunction(anvil.users,!)!2: "Sign up for a new account with the email address associated with the user's Facebook account. Prompts the user to authenticate with Facebook, then registers a new user with that email address. Raises anvil.users.UserExists if this email address is already registered; returns new user or None if cancelled." ["signup_with_facebook"]
	def signup_with_facebook(additional_scopes):
		if not _client_config.get("use_facebook"):
			raise Exception("Facebook signup is not enabled")

		if not _client_config.get("allow_signup"):
			raise Exception("New user signup is not enabled")

		import facbeook.auth
		if facbeook.auth.login(additional_scopes):
			return anvil.server.call("anvil.private.users.signup_with_facebook")

	# Disable documentation for raven functions for now.
	#defFunction(anvil.users,!)!2: "Log in with a Raven account. Prompts the user to authenticate with Raven, then logs in with their Raven account (if that user exists). Returns None if the login was cancelled or we have no record of this user." ["login_with_raven"]
	def login_with_raven():
		if not _client_config.get("use_raven"):
			raise Exception("Raven login is not enabled")

		import raven.auth
		if raven.auth.login():
			return anvil.server.call("anvil.private.users.login_with_raven")

	#defFunction(anvil.users,!)!2: "Sign up for a new account with the email address associated with the user's Raven account. Prompts the user to authenticate with Raven, then registers a new user with that email address. Raises anvil.users.UserExists if this email address is already registered; returns new user or None if cancelled." ["signup_with_raven"]
	def signup_with_raven():
		if not _client_config.get("use_raven"):
			raise Exception("Raven signup is not enabled")

		if not _client_config.get("allow_signup"):
			raise Exception("New user signup is not enabled")

		import raven.auth
		if raven.auth.login():
			return anvil.server.call("anvil.private.users.signup_with_raven")


	_label_style = {}

	#!defFunction(anvil.users,!)!2: "Display a sign-up form allowing a user to create a new account. Returns the new user object, or None if cancelled." ["signup_with_form"]
	def signup_with_form(_link_back_to_login_on_already_exists=False):
		if not _client_config.get("allow_signup"):
			raise Exception("New user signup is not enabled")

		lp = LinearPanel()
		email_box = None
		passwd_box = None

		def email_pressed_enter(**kws):
			if passwd_box and len(passwd_box) > 0:
				passwd_box[0].focus()

		def passwd_1_pressed_enter(**kws):
			if passwd_box and len(passwd_box) > 1:
				passwd_box[1].focus()

		def passwd_2_pressed_enter(**kws):
			lp.raise_event('x-close-alert', value='sign-up')

		if _client_config.get("use_email"):
			lp.add_component(Label(text="Email:", **_label_style))
			email_box = TextBox(placeholder="address@example.com")
			email_box.set_event_handler("pressed_enter", email_pressed_enter)
			lp.add_component(email_box)

		if _client_config.get("use_email"):
			passwd_box = [TextBox(hide_text=True, placeholder=p) for p in ["password", "repeat password"]]
			lp.add_component(Label(text="Password:", **_label_style))
			passwd_box[0].set_event_handler("pressed_enter", passwd_1_pressed_enter)
			lp.add_component(passwd_box[0])
			lp.add_component(Label(text="Retype password:", **_label_style))
			passwd_box[1].set_event_handler("pressed_enter", passwd_2_pressed_enter)
			lp.add_component(passwd_box[1])

		if _client_config.get("use_google"):
			import google.auth
			def google_login(**evt):
				if google.auth.login():
					lp.raise_event('x-close-alert', value='google')
			b = Button(text="Sign up with Google", icon="fa:google", icon_align="left")
			lp.add_component(b)
			b.set_event_handler("click", google_login)

		if _client_config.get("use_facebook"):
			import facebook.auth
			def facebook_login(**evt):
				if facebook.auth.login():
					lp.raise_event('x-close-alert', value='facebook')
			b = Button(text="Sign up with Facebook", icon="fa:facebook", icon_align="left")
			lp.add_component(b)
			b.set_event_handler("click", facebook_login)

		if _client_config.get("use_raven"):
			import raven.auth
			def raven_login(**evt):
				if raven.auth.login():
					lp.raise_event('x-close-alert', value='raven')
			b = Button(text="Sign up with Raven", icon="fa:lock", icon_align="left")
			lp.add_component(b)
			b.set_event_handler("click", raven_login)

		error_lbl = Label(foreground="red", bold=True, spacing_below="none")
		lp.add_component(error_lbl)

		log_in_instead_link = Link(text="Log in instead", visible=False,
								   icon="fa:chevron-right", icon_align="right", spacing_above="none")
		def log_in_instead(**evt):
			lp.raise_event('x-close-alert', value=None)
		log_in_instead_link.set_event_handler("click", log_in_instead)
		if _link_back_to_login_on_already_exists:
			lp.add_component(log_in_instead_link)

		while True:
			if passwd_box:
				for pb in passwd_box:
					pb.text = ""

			if _client_config.get("use_email"):
				ar = alert(lp, title="Sign Up", buttons=[("Sign Up", 'sign-up', "primary"), ("Cancel", None)])
			else:
				ar = alert(lp, title="Sign Up", buttons=[("Cancel", None)])

			if not ar:
				return None

			# TODO require certain fields and include them in the sign-up call

			try:
				if ar == 'google':
					user = anvil.server.call("anvil.private.users.signup_with_google")
				elif ar == 'facebook':
					user = anvil.server.call("anvil.private.users.signup_with_facebook")
				elif ar == 'raven':
					user = anvil.server.call("anvil.private.users.signup_with_raven")
				elif ar == 'sign-up' and passwd_box:
					if len(email_box.text) < 5 or "@" not in email_box.text or "." not in email_box.text:
						error_lbl.text = "Enter an email address"
						continue
					if passwd_box[1].text != passwd_box[0].text:
						error_lbl.text = "Passwords do not match"
						continue
					user = anvil.server.call("anvil.private.users.signup_with_email", email_box.text, passwd_box[0].text)
					if _client_config.get("confirm_email"):
						alert("We've sent a confirmation email to " + email_box.text + ". Open your inbox and click the link to complete your signup.", title="Confirm your Email", buttons=[("OK", None, "primary")])
				else:
					raise Exception("Invalid configuration for Users service")

			except UserExists as e:
				error_lbl.text = str(e.args[0])
				log_in_instead_link.visible = True
				continue

			return user


	#!defFunction(anvil.users,!)!2: "Display a login form and allow user to log in. Returns user object if logged in, or None if cancelled." ["login_with_form"]
	def login_with_form():
		lp = LinearPanel()
		email_box = None
		passwd_box = None

		def focus_password(**kws):
			passwd_box.focus()

		def close_alert(**kws):
			lp.raise_event('x-close-alert', value='login')

		if _client_config.get("use_email"):
			email_box = TextBox(placeholder="email@address.com")
			passwd_box = TextBox(placeholder="password", hide_text=True)

			email_box.set_event_handler("pressed_enter", focus_password)
			passwd_box.set_event_handler("pressed_enter", close_alert)

			lp.add_component(Label(text="Email:", **_label_style))
			lp.add_component(email_box)
			lp.add_component(Label(text="Password:", **_label_style))
			lp.add_component(passwd_box)

		if _client_config.get("use_google"):
			import google.auth
			def google_login(**evt):
				if google.auth.login():
					lp.raise_event('x-close-alert', value='google')
				
			b = Button(text="Log in with Google", icon="fa:google", icon_align="left")
			b.set_event_handler('click', google_login)
			lp.add_component(b)

		if _client_config.get("use_facebook"):
			import facebook.auth
			def facebook_login(**evt):
				if facebook.auth.login():
					lp.raise_event('x-close-alert', value='facebook')
				
			b = Button(text="Log in with Facebook", icon="fa:facebook", icon_align="left")
			b.set_event_handler('click', facebook_login)
			lp.add_component(b)

		if _client_config.get("use_raven"):
			import raven.auth
			def raven_login(**evt):
				if raven.auth.login():
					lp.raise_event('x-close-alert', value='raven')
				
			b = Button(text="Log in with Raven", icon="fa:lock", icon_align="left")
			b.set_event_handler('click', raven_login)
			lp.add_component(b)

		error_lbl = Label(foreground="red", bold=True)
		lp.add_component(error_lbl)

		def send_reset_email(**evt):
			send_password_reset_email(email_box.text)
			error_lbl.text = "Requested password reset for " + email_box.text + ". Check your email."
		reset_link = Link(text="Reset password by email", icon="fa:envelope", icon_align="right", visible=False)
		reset_link.set_event_handler('click', send_reset_email)
		lp.add_component(reset_link)

		if _client_config.get("allow_signup"):
			def open_signup(**evt):
				lp.raise_event('x-close-alert', value='sign-up')
			signup_link = Link(text="Sign up for a new account", icon="fa:user-plus")
			signup_link.set_event_handler('click', open_signup)
			lp.add_component(signup_link)

		while True:
			if passwd_box:
				passwd_box.text = ""
			if _client_config.get("use_email"):
				ar = alert(lp, title="Log In", buttons=[("Log In", 'login', 'success'), ("Cancel", None)])
			else:
				ar = alert(lp, title="Log In", buttons=[("Cancel", None)])

			try:
				if ar == 'google':
					return anvil.server.call("anvil.private.users.login_with_google")
				elif ar == 'facebook':
					return anvil.server.call("anvil.private.users.login_with_facebook")
				elif ar == 'raven':
					return anvil.server.call("anvil.private.users.login_with_raven")
				elif ar == 'login':
					try:
						return anvil.server.call("anvil.private.users.login_with_email", email_box.text, passwd_box.text)
					except AuthenticationFailed:
						reset_link.visible = True
						raise
				elif ar == 'sign-up':
					if signup_with_form(_link_back_to_login_on_already_exists=True):
						user = get_user()
						if user:
							return user
					# else continue around the loop
				else:
					return None
			except AuthenticationFailed as e:
				error_lbl.text = e.args[0]
