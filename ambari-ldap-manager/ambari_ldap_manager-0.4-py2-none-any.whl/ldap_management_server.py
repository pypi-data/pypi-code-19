from ldap_management import LdapManager
from flask import Flask, session, redirect, url_for, escape, request, render_template
import time
import json
import uuid
import sys

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex #a random string

@app.route('/', methods=['GET'])
def lambda_handler(event=None, context=None):
	session['ambari_url'] = ldap_mgr.ambari_url
	users = len(ldap_mgr.get_all_users().json()['items'])
	groups = len(ldap_mgr.get_all_groups().json()['items'])
	cluster = ldap_mgr.get_cluster_name()
	session['num_users'] = users
	session['num_groups'] = groups
	session['cluster'] = cluster
	return render_template('hello.html', session=session)

@app.route('/users', methods=['GET', 'POST'])
def users():
	if request.method == "POST":
		ldap_mgr.sync_user(request.form['uid'])
		users = ldap_mgr.get_all_users().json()
		return render_template('users.html', users=users)

	users = ldap_mgr.get_all_users().json()
	return render_template('users.html', users=users)

@app.route('/groups', methods=['GET', 'POST'])
def groups():
	if request.method == "POST":
		ldap_mgr.sync_group(request.form['gid'])
		groups = ldap_mgr.get_all_groups().json()
		return render_template('groups.html', groups=groups)

	groups = ldap_mgr.get_all_groups().json()
	return render_template('groups.html', groups=groups)

@app.route('/events', methods=['GET'])
def events():
	events = ldap_mgr.get_all_events().json()
	session['num_events'] = len(events['items'])
	return render_template('events.html', events=events)

@app.route('/delete_user/<string:del_user>', methods=['GET', 'POST'])
def delete_user(del_user):
	ldap_mgr.delete_user(del_user)
	users = ldap_mgr.get_all_users().json()
	return render_template('users.html', users=users)

@app.route('/sync_user/<string:sync_user>', methods=['GET', 'POST'])
def sync_user(sync_user):
	ldap_mgr.sync_user(sync_user)
	return redirect(url_for('users', get_user=sync_user))

@app.route('/delete_group/<string:del_group>', methods=['GET', 'POST'])
def delete_group(del_group):
	ldap_mgr.delete_group(del_group)
	groups = ldap_mgr.get_all_groups().json()
	return render_template('groups.html', groups=groups)

@app.route('/sync_group/<string:sync_group>', methods=['GET', 'POST'])
def sync_group(sync_group):
	ldap_mgr.sync_group(sync_group)
	return redirect(url_for('group', get_group=sync_group))

@app.route('/user/<string:get_user>', methods=['GET'])
def user(get_user):
	user_info = ldap_mgr.get_user(get_user).json()
	return render_template('user.html', user=user_info)

@app.route('/group/<string:get_group>', methods=['GET'])
def group(get_group):
	group_info = ldap_mgr.get_group(get_group).json()
	return render_template('group.html', group=group_info)

@app.route('/event/<string:get_event>', methods=['GET'])
def event(get_event):
	event_info = ldap_mgr.get_event(get_event).json()
	return render_template('event.html', event=event_info, session=session)

@app.template_filter('ctime')
def timectime(s):
    return time.ctime(int(s)) # datetime.datetime.fromtimestamp(s)

def main(args=None):
	if args is None:
		args = sys.argv
	if len(args) != 4:
		print("""Ambari LDAP Manager should be invokes as follows:
				python -m ambari-ldap-manager <http://ambari-host:8080> <username> <password>
			""")
		sys.exit(1)
	else:
		ambari_url = args[1]
		username = args[2]
		password = args[3]

		ldap_mgr = LdapManager(url=ambari_url, api="/api/v1", username=username, password=password)
		app.run()

if __name__ == '__main__':
	main()

