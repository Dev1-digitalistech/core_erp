import json
import frappe
import requests

@frappe.whitelist()
def fetch_from_stock_entry():
	stock_entries=frappe.get_all("Stock Entry",filters={'data_push':1,'docstatus':1})
	print(stock_entries)
	for stoc_ent in stock_entries:
		doc=frappe.get_doc("Stock Entry",stoc_ent)
		push_data_to_snd(doc)


@frappe.whitelist()
def push_data_to_snd(doc):
	if doc.items:
		for item in doc.items:
			send_to_snd(item,doc)

@frappe.whitelist()
def send_to_snd(item,doc):
	token=generate_token()
	if token:
		factory_code=frappe.db.get_value("Company",doc.company,"factory_code")
		fg_item=frappe.db.get_value("Item",item.item_code,["product_variant","product_category"],as_dict=1)
		if fg_item.product_category=="Chips":
			product_category="C"
		elif fg_item.product_category=="Namkeen":
			product_category="N"
		else:
			product_category="S"
	#	for word in doc.get('line').split():
	#		if word.isdigit():
	#			line=word
	#			break
		url=f"https://apps.dfmfoods.com/dfmwebapi/Prodction/productionentry?PrdM_FCd={factory_code}&PrdM_MRefNo={doc.name}&PrdM_PrdDt={doc.posting_date}&PrdM_ActDate={doc.posting_date}&PrdM_Narration={doc.remark}&PRDM_ITEMTYPE={product_category}&ItemCd={fg_item.product_variant}&ItemQty={int(item.qty)}&tockenNo={token}"

		try:
			response=requests.request("GET",url)
		except Exception as e:
			frappe.throw(e)
		resp=json.loads(response.text)
		frappe.msgprint(str(resp))
		if resp.get('IsSuccess')==True and resp.get('Status')==True and resp.get('Message')=="Production Entry Has Been Inserted Successfully.":
			frappe.db.sql('''update `tabStock Entry` set data_pushed=1 where name=%(name)s''',{"name":doc.name},as_dict=1)
			frappe.log_error(resp,"Pushed")
		else:
			frappe.log_error(resp,"Response received")


@frappe.whitelist()
def generate_token():
	url="https://apps.dfmfoods.com/dfmwebapi/Prodction/gettoken?userid=erpNext&password=DFM@2021"
	try:
		response=requests.request("GET",url)
	except Exception as e:
		frappe.log_error(e,'token error')
		raise(e)

	resp=json.loads(response.text)
	if resp.get('IsSuccess')==True and resp.get('Status')==True:
		return resp.get('Data')
	else:
		frappe.log_error(resp,"SND Error")
