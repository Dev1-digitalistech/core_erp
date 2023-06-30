import frappe

# for auto-disabling users 
# @frappe.whitelist()
# def auto_disable_users():
# 	from datetime import date,timedelta
# 	yesterday = date.today()+timedelta(days=-1)
# 	print(yesterday)
# 	frappe.db.sql("""update `tabUser` set enabled = 0 where last_working_day <= %s and enabled = 1""",yesterday)

# TODO: add to doc event for ToDo
# for todo.py 
def before_save(self, method=None):
	frappe.db.set_value('Issue', self.reference_name, 'assign_to', self.owner)


# EmailAccount email.py changes for issue 
def create_new_parent(self, communication, email):
		'''If no parent found, create a new reference document'''

		# no parent found, but must be tagged
		# insert parent type doc
		parent = frappe.new_doc(self.append_to)
		# frappe.log_error(self.email_account,"issue_support")

		#to email account set
		parent.to_email_account=self.email_account

		if self.subject_field:
			parent.set(self.subject_field, frappe.as_unicode(email.subject)[:140])

		if self.sender_field:
			parent.set(self.sender_field, frappe.as_unicode(email.from_email))

		if parent.meta.has_field("email_account"):
			parent.email_account = self.name

		if self.append_to == 'Issue':
			parent.source_of_input = "Email"

		parent.flags.ignore_mandatory = True

		try:
			parent.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError:
			# try and find matching parent
			parent_name = frappe.db.get_value(self.append_to, {self.sender_field: email.from_email})
			if parent_name:
				parent.name = parent_name
			else:
				parent = None

		# NOTE if parent isn't found and there's no subject match, it is likely that it is a new conversation thread and hence is_first = True
		communication.is_first = True

		return parent

@frappe.whitelist()
def _create_reference_document_dup(self, doctype):
		"""Create reference document if it does not exist in the system."""
		parent = frappe.new_doc(doctype)
		email_fileds = self.get_email_fields(doctype)
		frappe.log_error("issue tickets",str(self))

		if email_fileds.subject_field:
			parent.set(email_fileds.subject_field, frappe.as_unicode(self.subject)[:140])

		if email_fileds.sender_field:
			parent.set(email_fileds.sender_field, frappe.as_unicode(self.from_email))
		
		

		if(doctype == "Issue"):
			string = str(self.email_account)
			substring = string.split('(')[1].split(')')[0]
			parent.set("to_email_account",substring)
			parent.source_of_input = "Email"
			parent.set("description",self.content)
			parent.email_id=str(self.from_email)			
		# frappe.log_error(self,"issue tickets")

		parent.flags.ignore_mandatory = True

		try:
			parent.insert(ignore_permissions=True)
		except frappe.DuplicateEntryError:
			# try and find matching parent
			parent_name = frappe.db.get_value(
				self.email_account.append_to, {email_fileds.sender_field: self.from_email}
			)
			if parent_name:
				parent.name = parent_name
			else:
				parent = None
		return parent
