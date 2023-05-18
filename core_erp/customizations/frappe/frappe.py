
# from __future__ import unicode_literals, print_function
# import frappe
# import imaplib
# import re
# import json
# import socket
# from frappe import _
# from frappe.model.document import Document
# from frappe.utils import validate_email_address, cstr, cint, get_datetime, DATE_FORMAT, strip, comma_or, sanitize_html, add_days
# from frappe.utils.user import is_system_user
# from frappe.utils.jinja import render_template
# from frappe.email.smtp import SMTPServer
# from frappe.email.receive import EmailServer, Email
# from poplib import error_proto
# from dateutil.relativedelta import relativedelta
# from datetime import datetime, timedelta
# from frappe.desk.form import assign_to
# from frappe.utils.user import get_system_managers
# from frappe.utils.background_jobs import enqueue, get_jobs
# from frappe.core.doctype.communication.email import set_incoming_outgoing_accounts
# # from frappe.utils.scheduler import log
# from frappe.utils.html_utils import clean_email_html
# from frappe.email.utils import get_port



# class SentEmailInInbox(Exception):
# 	pass

# # for auto-disabling users 
# @frappe.whitelist()
# def auto_disable_users():
# 	from datetime import date,timedelta
# 	yesterday = date.today()+timedelta(days=-1)
# 	print(yesterday)
# 	frappe.db.sql("""update `tabUser` set enabled = 0 where last_working_day <= %s and enabled = 1""",yesterday)

# # TODO: add to doc event for ToDo
# # for todo.py 
# def before_save(self, method=None):
# 	frappe.db.set_value('Issue', self.reference_name, 'assign_to', self.owner)


# # EmailAccount email.py changes for issue 
# def create_new_parent(self, communication, email):
# 		'''If no parent found, create a new reference document'''

# 		# no parent found, but must be tagged
# 		# insert parent type doc
# 		parent = frappe.new_doc(self.append_to)
# 		frappe.log_error(self.email_account,"issue_support")

# 		#to email account set
# 		parent.to_email_account=self.email_account

# 		if self.subject_field:
# 			parent.set(self.subject_field, frappe.as_unicode(email.subject)[:140])

# 		if self.sender_field:
# 			parent.set(self.sender_field, frappe.as_unicode(email.from_email))

# 		if parent.meta.has_field("email_account"):
# 			parent.email_account = self.name

# 		if self.append_to == 'Issue':
# 			parent.source_of_input = "Email"

# 		parent.flags.ignore_mandatory = True

# 		try:
# 			parent.insert(ignore_permissions=True)
# 		except frappe.DuplicateEntryError:
# 			# try and find matching parent
# 			parent_name = frappe.db.get_value(self.append_to, {self.sender_field: email.from_email})
# 			if parent_name:
# 				parent.name = parent_name
# 			else:
# 				parent = None

# 		# NOTE if parent isn't found and there's no subject match, it is likely that it is a new conversation thread and hence is_first = True
# 		communication.is_first = True

# 		return parent



# def set_thread(self, communication, email):
# 	"""Appends communication to parent based on thread ID. Will extract
# 	parent communication and will link the communication to the reference of that
# 	communication. Also set the status of parent transaction to Open or Replied.

# 	If no thread id is found and `append_to` is set for the email account,
# 	it will create a new parent transaction (e.g. Issue)"""
# 	parent = None

# 	parent = self.find_parent_from_in_reply_to(communication, email)

# 	if not parent and self.append_to:
# 		self.set_sender_field_and_subject_field()

# 	if not parent and self.append_to:
# 		parent = self.find_parent_based_on_subject_and_sender(communication, email)

# 	if not parent and self.append_to and self.append_to!="Communication":
# 		parent = self.create_new_parent(communication, email)


# 	if parent:
# 		communication.reference_doctype = parent.doctype
# 		communication.reference_name = parent.name

# 	# check if message is notification and disable notifications for this message
# 	isnotification = email.mail.get("isnotification")
# 	if isnotification:
# 		if "notification" in isnotification:
# 			communication.unread_notification_sent = 1



# def insert_communication(self, msg, args=None):
# 	if isinstance(msg, list):
# 		raw, uid, seen = msg
# 	else:
# 		raw = msg
# 		uid = -1
# 		seen = 0
# 	if isinstance(args, dict):
# 		if args.get("uid", -1): uid = args.get("uid", -1)
# 		if args.get("seen", 0): seen = args.get("seen", 0)

# 	email = Email(raw)

# 	if email.from_email == self.email_id and not email.mail.get("Reply-To"):
# 		# gmail shows sent emails in inbox
# 		# and we don't want emails sent by us to be pulled back into the system again
# 		# dont count emails sent by the system get those
# 		if frappe.flags.in_test:
# 			print('WARN: Cannot pull email. Sender sames as recipient inbox')
# 		raise SentEmailInInbox

# 	if email.message_id:
# 		# https://stackoverflow.com/a/18367248
# 		names = frappe.db.sql("""SELECT DISTINCT `name`, `creation` FROM `tabCommunication`
# 			WHERE `message_id`='{message_id}'
# 			ORDER BY `creation` DESC LIMIT 1""".format(
# 				message_id=email.message_id
# 			), as_dict=True)

# 		if names:
# 			name = names[0].get("name")
# 			# email is already available update communication uid instead
# 			frappe.db.set_value("Communication", name, "uid", uid, update_modified=False)

# 			self.flags.notify = False

# 			return frappe.get_doc("Communication", name)

# 	if email.content_type == 'text/html':
# 		email.content = clean_email_html(email.content)

# 	communication = frappe.get_doc({
# 		"doctype": "Communication",
# 		"subject": email.subject,
# 		"content": email.content,
# 		'text_content': email.text_content,
# 		"sent_or_received": "Received",
# 		"sender_full_name": email.from_real_name,
# 		"sender": email.from_email,
# 		"recipients": email.mail.get("To"),
# 		"cc": email.mail.get("CC"),
# 		"email_account": self.name,
# 		"communication_medium": "Email",
# 		"uid": int(uid or -1),
# 		"message_id": email.message_id,
# 		"communication_date": email.date,
# 		"has_attachment": 1 if email.attachments else 0,
# 		"seen": seen or 0
# 	})

# 	self.set_thread(communication, email)
# 	if communication.seen:
# 		# get email account user and set communication as seen
# 		users = frappe.get_all("User Email", filters={ "email_account": self.name },
# 			fields=["parent"])
# 		users = list(set([ user.get("parent") for user in users ]))
# 		communication._seen = json.dumps(users)

# 	communication.flags.in_receive = True
# 	communication.insert(ignore_permissions=True)

# 	# save attachments
# 	communication._attachments = email.save_attachments_in_doc(communication)

# 	# replace inline images
# 	dirty = False
# 	for file in communication._attachments:
# 		if file.name in email.cid_map and email.cid_map[file.name]:
# 			dirty = True

# 			email.content = email.content.replace("cid:{0}".format(email.cid_map[file.name]),
# 				file.file_url)

# 	if dirty:
# 		# not sure if using save() will trigger anything
# 		communication.db_set("content", sanitize_html(email.content))

# 	# notify all participants of this thread
# 	if self.enable_auto_reply and getattr(communication, "is_first", False):
# 		self.send_auto_reply(communication, email)

# 	return communication



# @frappe.whitelist()
# def receive_dup(self, test_mails=None):
# 		"""Called by scheduler to receive emails from this EMail account using POP3/IMAP."""
# 		def get_seen(status):
# 			if not status:
# 				return None
# 			seen = 1 if status == "SEEN" else 0
# 			return seen

# 		if self.enable_incoming:
# 			uid_list = []
# 			exceptions = []
# 			seen_status = []
# 			uid_reindexed = False

# 			if frappe.local.flags.in_test:
# 				incoming_mails = test_mails
# 			else:
# 				email_sync_rule = self.build_email_sync_rule()

# 				email_server = None
# 				try:
# 					email_server = self.get_incoming_server(in_receive=True, email_sync_rule=email_sync_rule)
# 				except Exception:
# 					frappe.log_error(title=_("Error while connecting to email account {0}").format(self.name))

# 				if not email_server:
# 					return

# 				emails = email_server.get_messages()
# 				if not emails:
# 					return

# 				incoming_mails = emails.get("latest_messages", [])
# 				uid_list = emails.get("uid_list", [])
# 				seen_status = emails.get("seen_status", [])
# 				uid_reindexed = emails.get("uid_reindexed", False)

# 			for idx, msg in enumerate(incoming_mails):
# 				uid = None if not uid_list else uid_list[idx]
# 				self.flags.notify = True

# 				try:
# 					args = {
# 						"uid": uid,
# 						"seen": None if not seen_status else get_seen(seen_status.get(uid, None)),
# 						"uid_reindexed": uid_reindexed
# 					}
# 					communication = self.insert_communication(msg, args=args)

# 				except SentEmailInInbox:
# 					frappe.db.rollback()

# 				except Exception:
# 					frappe.db.rollback()
# 					# log('email_account.receive')
# 					if self.use_imap:
# 						self.handle_bad_emails(email_server, uid, msg, frappe.get_traceback())
# 					exceptions.append(frappe.get_traceback())

# 				else:
# 					frappe.db.commit()
# 					if communication and self.flags.notify:

# 						# If email already exists in the system
# 						# then do not send notifications for the same email.

# 						attachments = []
# 						if hasattr(communication, '_attachments'):
# 							attachments = [d.file_name for d in communication._attachments]

# 						communication.notify(attachments=attachments, fetched_from_email_account=True)

# 			#notify if user is linked to account
# 			if len(incoming_mails)>0 and not frappe.local.flags.in_test:
# 				frappe.publish_realtime('new_email', {"account":self.email_account_name, "number":len(incoming_mails)})

# 			if exceptions:
# 				raise Exception(frappe.as_json(exceptions))
