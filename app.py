from flask import Flask, request, jsonify, make_response, session, redirect, url_for
import pymysql
import pymysql.cursors
import json

app = Flask(__name__)
app.secret_key = 'ucsp_secret_2026'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

DB = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ucsp_db',
    'port': 3306,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'ssl_disabled': True
}

def get_db():
    con = pymysql.connect(**DB)
    try:
        with con.cursor() as cur:
            cur.execute("SET SESSION max_allowed_packet=67108864")
    except: pass
    return con

def date_str(row, fields):
    for f in fields:
        if row.get(f): row[f] = str(row[f])
    return row

@app.route('/')
def index():
    resp = make_response(open(app.template_folder+'/index.html','r',encoding='utf-8').read())
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-store'
    return resp

# ── LOGIN ──────────────────────────────────────────────────────────
@app.route('/api/login/admin', methods=['POST'])
def login_admin():
    try:
        d = request.json
        if not d: return jsonify({'ok': False, 'msg': 'No data'})
        con = get_db()
        try:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (d['username'], d['password']))
                user = cur.fetchone()
            if user: return jsonify({'ok': True, 'name': user['name']})
            return jsonify({'ok': False, 'msg': 'Invalid credentials'})
        finally: con.close()
    except Exception as ex:
        import traceback; traceback.print_exc()
        return jsonify({'ok': False, 'msg': str(ex)}), 200

@app.route('/api/login/faculty', methods=['POST'])
def login_faculty():
    try:
        d = request.json
        if not d: return jsonify({'ok': False, 'msg': 'No data'})
        con = get_db()
        try:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM faculty WHERE username=%s AND password=%s AND dept=%s", (d['username'], d['password'], d['dept']))
                user = cur.fetchone()
            if not user: return jsonify({'ok': False, 'msg': 'Invalid credentials or wrong department'})
            if user.get('created_at'): user['created_at'] = str(user['created_at'])
            session['faculty'] = {k: (v.strftime('%Y-%m-%d') if hasattr(v,'year') else v) for k,v in user.items() if k != 'photo'}
            safe_f = {k:v for k,v in user.items() if k not in ('photo','file_data') and not isinstance(v,bytes)}
            return jsonify({'ok': True, 'faculty': safe_f, 'redirect': '/faculty'})
        finally: con.close()
    except Exception as ex:
        import traceback; traceback.print_exc()
        return jsonify({'ok': False, 'msg': str(ex)}), 200

@app.route('/api/login/student', methods=['POST'])
def login_student():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE username=%s AND password=%s AND dept=%s", (d['username'], d['password'], d['dept']))
            user = cur.fetchone()
        if not user: return jsonify({'ok': False, 'msg': 'Invalid credentials'})
        if user.get('created_at'): user['created_at'] = str(user['created_at'])
        session['student'] = {k: (v.strftime('%Y-%m-%d') if hasattr(v,'year') else v) for k,v in user.items() if k != 'photo'}
        safe = {k:v for k,v in user.items() if k not in ('photo','file_data') and not isinstance(v,bytes)}
        return jsonify({'ok': True, 'student': safe, 'redirect': '/student'})
    finally: con.close()

# ── DATA ────────────────────────────────────────────────────────────
@app.route('/api/data')
def get_data():
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM faculty")
            faculty = cur.fetchall()
            for f in faculty:
                if f.get('created_at'): f['created_at'] = str(f['created_at'])
            cur.execute("SELECT * FROM students")
            students = cur.fetchall()
            for s in students:
                if s.get('created_at'): s['created_at'] = str(s['created_at'])
            cur.execute("SELECT * FROM bus_routes")
            bus = cur.fetchall()
            cur.execute("SELECT * FROM events ORDER BY date DESC")
            events = cur.fetchall()
            for e in events:
                if e.get('date'): e['date'] = str(e['date'])
            cur.execute("SELECT * FROM placed")
            placed = cur.fetchall()
            cur.execute("SELECT * FROM rank_holders ORDER BY rank_no")
            rank = cur.fetchall()
            cur.execute("SELECT * FROM updates ORDER BY created_at DESC")
            updates = cur.fetchall()
            for u in updates:
                if u.get('created_at'): u['created_at'] = str(u['created_at'])
            cur.execute("SELECT * FROM admins")
            admins = cur.fetchall()
        return jsonify({'faculty':faculty,'students':students,'bus':bus,'events':events,
                        'placed':placed,'rank':rank,'updates':updates,'admins':admins})
    finally: con.close()

# ── FACULTY CRUD ────────────────────────────────────────────────────
@app.route('/api/faculty', methods=['POST'])
def add_faculty():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO faculty (username,password,name,role,dept,phone,experience,photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (d['un'],d['pw'],d['nm'],d.get('role','Assistant Professor'),d['dept'],d.get('ph',''),d.get('exp',''),d.get('photo','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})
    finally: con.close()

@app.route('/api/faculty/<int:fid>', methods=['DELETE'])
def del_faculty(fid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM faculty WHERE id=%s", (fid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── STUDENT CRUD ────────────────────────────────────────────────────
@app.route('/api/students', methods=['POST'])
def add_student():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO students (username,password,name,reg_no,dept,year,section,email,phone,photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d['username'],d['password'],d['name'],d['reg_no'],d['dept'],d.get('year','1st Year'),d.get('section','A'),d.get('email',''),d.get('phone',''),d.get('photo','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})
    finally: con.close()

@app.route('/api/students/<int:sid>', methods=['DELETE'])
def del_student(sid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM students WHERE id=%s", (sid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── BUS, EVENTS, PLACED, RANK, UPDATES ─────────────────────────────
@app.route('/api/bus', methods=['POST'])
def add_bus():
    try:
        d = request.json
        if not d or not d.get('lb'): return jsonify({'ok':False,'msg':'No label'})
        con = get_db()
        try:
            with con.cursor() as cur:
                cur.execute("INSERT INTO bus_routes (label,date_str,inbound,outbound) VALUES (%s,%s,%s,%s)",
                    (d['lb'],d.get('dt',''),d.get('inn',''),d.get('out','')))
                con.commit()
                return jsonify({'ok': True, 'id': cur.lastrowid})
        finally: con.close()
    except Exception as ex:
        import traceback; traceback.print_exc()
        return jsonify({'ok': False, 'msg': str(ex)}), 200

@app.route('/api/bus/<int:bid>', methods=['DELETE'])
def del_bus(bid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM bus_routes WHERE id=%s", (bid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

@app.route('/api/events', methods=['POST'])
def add_event():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO events (name,date,dept,photo) VALUES (%s,%s,%s,%s)",
                (d['nm'],d.get('dt'),d.get('dept','All'),d.get('photo','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/events/<int:eid>', methods=['DELETE'])
def del_event(eid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM events WHERE id=%s", (eid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

@app.route('/api/placed', methods=['POST'])
def add_placed():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO placed (name,company,package,dept,photo,year) VALUES (%s,%s,%s,%s,%s,%s)",
                (d.get('nm',d.get('name','')),d.get('co',d.get('company','')),d.get('ctc',d.get('pkg',d.get('package',''))),d.get('dept',''),d.get('photo',''),d.get('yr',d.get('year',''))))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/placed/<int:pid>', methods=['DELETE'])
def del_placed(pid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM placed WHERE id=%s", (pid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

@app.route('/api/rank', methods=['POST'])
def add_rank():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO rank_holders (name,rank_no,cgpa,dept,year,photo) VALUES (%s,%s,%s,%s,%s,%s)",
                (d.get('nm',d.get('name','')),d.get('rno',d.get('rk',1)),d.get('cgpa',0),d.get('dept',''),d.get('yr',d.get('year','')),d.get('photo','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/rank/<int:rid>', methods=['DELETE'])
def del_rank(rid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM rank_holders WHERE id=%s", (rid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

@app.route('/api/updates', methods=['POST'])
def add_update():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO updates (message,type,dept) VALUES (%s,%s,%s)", (d['msg'],d.get('type','info'),d.get('dept','All')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/updates/<int:uid>', methods=['DELETE'])
def del_update(uid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM updates WHERE id=%s", (uid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── ATTENDANCE ──────────────────────────────────────────────────────
@app.route('/api/attendance', methods=['POST'])
def save_attendance():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            for rec in d.get('records', []):
                cur.execute("INSERT INTO attendance (student_id,student_name,dept,subject,att_date,period,status) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE status=%s",
                    (rec['student_id'],rec['student_nm'],rec['dept'],rec['subject'],rec['date'],rec['period'],rec['status'],rec['status']))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    con = get_db()
    try:
        with con.cursor() as cur:
            student_id = request.args.get('student_id','')
            dept       = request.args.get('dept','')
            subject    = request.args.get('subject','')
            date       = request.args.get('date','')
            if student_id:
                # Student view — all their own attendance
                cur.execute("SELECT * FROM attendance WHERE student_id=%s ORDER BY att_date DESC, period", (student_id,))
            elif dept and date and not subject:
                # Faculty load view — all subjects for this date (for period lock)
                cur.execute("SELECT * FROM attendance WHERE dept=%s AND att_date=%s ORDER BY period",
                    (dept, date))
            elif dept and subject and date:
                # Faculty marking view — specific subject
                cur.execute("SELECT * FROM attendance WHERE dept=%s AND subject=%s AND att_date=%s ORDER BY period",
                    (dept, subject, date))
            else:
                cur.execute("SELECT * FROM attendance WHERE dept=%s ORDER BY att_date DESC", (dept,))
            rows = cur.fetchall()
        for r in rows:
            if r.get('att_date'): r['att_date'] = str(r['att_date'])
        return jsonify(rows)
    finally: con.close()

# ── AVG ATTENDANCE ──────────────────────────────────────────────────
@app.route('/api/attendance/avg', methods=['GET'])
def get_avg_attendance():
    dept = request.args.get('dept','')
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='Present' OR status='P' THEN 1 ELSE 0 END) as present FROM attendance WHERE dept=%s", (dept,))
            row = cur.fetchone()
            total = row['total'] or 0
            present = row['present'] or 0
            avg = round(present/total*100) if total > 0 else 0
        return jsonify({'ok': True, 'avg': avg, 'total': total, 'present': present})
    except Exception as ex:
        return jsonify({'ok': False, 'avg': 0, 'msg': str(ex)})
    finally: con.close()

# ── AVG ATTENDANCE ──────────────────────────────────────────────────
# ── MARKS ───────────────────────────────────────────────────────────
@app.route('/api/marks', methods=['GET'])
def get_marks():
    con = get_db()
    try:
        with con.cursor() as cur:
            student_id = request.args.get('student_id')
            dept = request.args.get('dept','')
            subject = request.args.get('subject','')
            year = request.args.get('year','')
            if student_id:
                cur.execute("SELECT * FROM marks WHERE student_id=%s ORDER BY subject,exam_type", (student_id,))
            elif dept and subject:
                cur.execute("SELECT * FROM marks WHERE dept=%s AND subject=%s ORDER BY student_name,exam_type", (dept, subject))
            elif dept and year:
                cur.execute("SELECT * FROM marks WHERE dept=%s AND student_name IN (SELECT name FROM students WHERE dept=%s AND year=%s) ORDER BY student_name,subject,exam_type", (dept, dept, year))
            else:
                cur.execute("SELECT * FROM marks WHERE dept=%s ORDER BY student_name,subject,exam_type", (dept,))
            rows = cur.fetchall()
        return jsonify(rows)
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500
    finally: con.close()

@app.route('/api/marks', methods=['POST'])
def save_marks():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            for rec in d.get('records', []):
                cur.execute("INSERT INTO marks (student_id,student_name,dept,subject,exam_type,mark,max_mark) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE mark=%s,max_mark=%s",
                    (rec['student_id'],rec['student_nm'],rec['dept'],rec['subject'],rec['exam_type'],rec['mark'],rec['max_mark'],rec['mark'],rec['max_mark']))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── LEAVES ──────────────────────────────────────────────────────────
@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    con = get_db()
    try:
        with con.cursor() as cur:
            fid = request.args.get('faculty_id')
            if fid:
                cur.execute("SELECT * FROM leaves WHERE faculty_id=%s ORDER BY applied_on DESC", (fid,))
            else:
                cur.execute("SELECT * FROM leaves ORDER BY applied_on DESC")
            rows = cur.fetchall()
        for r in rows:
            date_str(r, ['from_date','to_date','applied_on'])
        return jsonify(rows)
    finally: con.close()

@app.route('/api/leaves', methods=['POST'])
def apply_leave():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            fid = int(d.get('faculty_id') or 0)
            fnm = d.get('faculty_nm') or d.get('faculty_name','')
            fdept = d.get('faculty_dept','')
            if not fid and fnm:
                cur.execute("SELECT id FROM faculty WHERE name=%s OR nm=%s LIMIT 1", (fnm, fnm))
                row = cur.fetchone()
                if row: fid = row['id']
            # Check which columns exist in leaves table
            cur.execute("SHOW COLUMNS FROM leaves")
            cols = [r['Field'] for r in cur.fetchall()]
            if 'faculty_name' in cols and 'faculty_dept' in cols:
                cur.execute("INSERT INTO leaves (faculty_id,faculty_name,faculty_dept,leave_type,from_date,to_date,days,reason) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (fid, fnm, fdept, d.get('leave_type',''), d.get('from_date',''), d.get('to_date',''), d.get('days',1), d.get('reason','')))
            else:
                # Add missing columns first
                if 'faculty_name' not in cols:
                    cur.execute("ALTER TABLE leaves ADD COLUMN faculty_name VARCHAR(100)")
                if 'faculty_dept' not in cols:
                    cur.execute("ALTER TABLE leaves ADD COLUMN faculty_dept VARCHAR(100)")
                cur.execute("INSERT INTO leaves (faculty_id,faculty_name,faculty_dept,leave_type,from_date,to_date,days,reason) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (fid, fnm, fdept, d.get('leave_type',''), d.get('from_date',''), d.get('to_date',''), d.get('days',1), d.get('reason','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/api/leaves/<int:lid>', methods=['PUT'])
def update_leave(lid):
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("UPDATE leaves SET status=%s WHERE id=%s", (d['status'], lid))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

@app.route('/api/leaves/<int:lid>', methods=['DELETE'])
def delete_leave(lid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM leaves WHERE id=%s", (lid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── NOTES ───────────────────────────────────────────────────────────
@app.route('/api/notes', methods=['GET'])
def get_notes():
    con = get_db()
    try:
        with con.cursor() as cur:
            dept = request.args.get('dept','')
            cur.execute("SELECT id,faculty_id,faculty_name,dept,title,description,year_group,section,file_name,file_data,file_mime,posted_on FROM notes WHERE dept=%s ORDER BY posted_on DESC", (dept,))
            rows = cur.fetchall()
        for r in rows:
            if r.get('posted_on'): r['posted_on'] = str(r['posted_on'])
        return jsonify(rows)
    finally: con.close()

@app.route('/api/notes/<int:nid>/file', methods=['GET'])
def get_note_file(nid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT file_data,file_mime,file_name FROM notes WHERE id=%s", (nid,))
            row = cur.fetchone()
        if not row or not row['file_data']:
            return jsonify({'ok': False, 'msg': 'No file'}), 200
        return jsonify({'ok': True, 'file_data': row['file_data'], 'file_mime': row['file_mime'], 'file_name': row['file_name']})
    finally: con.close()

@app.route('/api/notes', methods=['POST'])
def add_note():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO notes (faculty_id,faculty_name,dept,title,description,year_group,section,file_name,file_data,file_mime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d['faculty_id'],d['faculty_nm'],d['dept'],d['title'],d.get('description',''),d.get('year_group','All'),d.get('section','All'),d.get('file_name',''),d.get('file_data',''),d.get('file_mime','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/notes/<int:nid>', methods=['DELETE'])
def del_note(nid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id=%s", (nid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── ASSIGNMENTS ─────────────────────────────────────────────────────
@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    con = get_db()
    try:
        with con.cursor() as cur:
            dept = request.args.get('dept','')
            cur.execute("SELECT * FROM assignments WHERE dept=%s ORDER BY posted_on DESC", (dept,))
            rows = cur.fetchall()
        for r in rows:
            date_str(r, ['due_date','posted_on'])
        return jsonify(rows)
    finally: con.close()

@app.route('/api/assignments', methods=['POST'])
def add_assignment():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO assignments (faculty_id,faculty_name,dept,title,subject,due_date,year_group,section,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d['faculty_id'],d['faculty_nm'],d['dept'],d['title'],d.get('subject',''),d.get('due_date'),d.get('year_group','All'),d.get('section','All'),d.get('description','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/assignments/<int:aid>', methods=['DELETE'])
def del_assignment(aid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM assignments WHERE id=%s", (aid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── SUBMISSIONS ─────────────────────────────────────────────────────
@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    con = get_db()
    try:
        with con.cursor() as cur:
            aid = request.args.get('assignment_id')
            sid = request.args.get('student_id')
            if sid:
                cur.execute("SELECT id,assignment_id,student_id,student_name,file_name,mark,grade,feedback,submitted_on FROM submissions WHERE student_id=%s", (sid,))
            elif aid:
                cur.execute("SELECT id,assignment_id,student_id,student_name,file_name,file_data,mark,grade,feedback,submitted_on FROM submissions WHERE assignment_id=%s", (aid,))
            else:
                return jsonify([])
            rows = cur.fetchall()
        for r in rows:
            if r.get('submitted_on'): r['submitted_on'] = str(r['submitted_on'])
        return jsonify(rows)
    finally: con.close()

@app.route('/api/submissions/<int:aid>/<int:sid>', methods=['PUT'])
def save_submission_mark(aid, sid):
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO submissions (assignment_id,student_id,student_name,mark) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE mark=%s,grade=%s",
                (aid, sid, d.get('student_name',''), d.get('mark'), d.get('mark'), d.get('grade','')))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── TIMETABLE CONFIG ────────────────────────────────────────────────
@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    con = get_db()
    try:
        with con.cursor() as cur:
            dept = request.args.get('dept','')
            cur.execute("SELECT * FROM timetable_config WHERE dept=%s", (dept,))
            rows = cur.fetchall()
        result = {}
        for r in rows:
            key = r['dept'] + '|' + str(r['year_no']) + '|' + r.get('section','A')
            result[key] = json.loads(r['config_json'])
        return jsonify(result)
    finally: con.close()

@app.route('/api/timetable', methods=['POST'])
def save_timetable():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            sect = d.get('section','A')
            # Try with section column first, fallback to without
            try:
                cur.execute("INSERT INTO timetable_config (dept,year_no,section,config_json) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE config_json=%s",
                    (d['dept'], d['year_no'], sect, json.dumps(d['config']), json.dumps(d['config'])))
            except Exception:
                # section column doesn't exist yet - auto-add it
                try:
                    cur.execute("ALTER TABLE timetable_config ADD COLUMN section VARCHAR(5) NOT NULL DEFAULT 'A'")
                    cur.execute("ALTER TABLE timetable_config DROP INDEX uniq_tt")
                    cur.execute("ALTER TABLE timetable_config ADD UNIQUE KEY uniq_tt (dept, year_no, section)")
                except Exception:
                    pass
                cur.execute("INSERT INTO timetable_config (dept,year_no,section,config_json) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE config_json=%s",
                    (d['dept'], d['year_no'], sect, json.dumps(d['config']), json.dumps(d['config'])))
            con.commit()
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/faculty')
def faculty_page():
    if 'faculty' not in session:
        return redirect('/')
    resp = make_response(open(app.template_folder+'/faculty.html','r',encoding='utf-8').read())
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-store'
    return resp

@app.route('/api/faculty/session')
def faculty_session():
    if 'faculty' not in session:
        return jsonify({'ok': False})
    return jsonify({'ok': True, 'faculty': session['faculty']})

@app.route('/api/faculty/logout', methods=['POST'])
def faculty_logout():
    session.pop('faculty', None)
    return jsonify({'ok': True})

@app.route('/student')
def student_page():
    if 'student' not in session:
        return redirect('/')
    resp = make_response(open(app.template_folder+'/student.html','r',encoding='utf-8').read())
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Cache-Control'] = 'no-store'
    return resp

@app.route('/api/student/session')
def student_session():
    if 'student' not in session:
        return jsonify({'ok': False})
    return jsonify({'ok': True, 'student': session['student']})

@app.route('/api/student/photo')
def student_photo():
    if 'student' not in session:
        return jsonify({'ok': False})
    sid = session['student'].get('id')
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT photo FROM students WHERE id=%s", (sid,))
            row = cur.fetchone()
        if row and row.get('photo'):
            return jsonify({'ok': True, 'photo': row['photo']})
        return jsonify({'ok': True, 'photo': None})
    finally: con.close()

@app.route('/api/student/logout', methods=['POST'])
def student_logout():
    session.pop('student', None)
    return jsonify({'ok': True})

# ── STUDENT LEAVES ──────────────────────────────────────────────────
@app.route('/api/student_leaves', methods=['GET'])
def get_student_leaves():
    con = get_db()
    try:
        with con.cursor() as cur:
            sid = request.args.get('student_id')
            dept = request.args.get('dept')
            if sid:
                cur.execute("SELECT * FROM student_leaves WHERE student_id=%s ORDER BY applied_on DESC", (sid,))
            elif dept:
                cur.execute("SELECT * FROM student_leaves WHERE student_dept=%s ORDER BY applied_on DESC", (dept,))
            else:
                cur.execute("SELECT * FROM student_leaves ORDER BY applied_on DESC")
            rows = cur.fetchall()
            for r in rows:
                for k in ['from_date','to_date','applied_on']:
                    if r.get(k): r[k] = str(r[k])
            return jsonify(rows)
    finally: con.close()

@app.route('/api/student_leaves', methods=['POST'])
def apply_student_leave():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO student_leaves (student_id,student_name,student_reg,student_dept,student_year,student_section,leave_type,from_date,to_date,days,reason) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d.get('student_id'), d.get('student_name',''), d.get('student_reg',''), d.get('student_dept',''), d.get('student_year',''), d.get('student_section',''), d.get('leave_type',''), d.get('from_date'), d.get('to_date'), d.get('days',1), d.get('reason','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/api/student_leaves/<int:lid>', methods=['PUT'])
def update_student_leave(lid):
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("UPDATE student_leaves SET status=%s WHERE id=%s", (d['status'], lid))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── EXAM SCHEDULE ────────────────────────────────────────────────────
@app.route('/api/exam_schedule', methods=['GET'])
def get_exam_schedule():
    con = get_db()
    try:
        with con.cursor() as cur:
            dept = request.args.get('dept','')
            cur.execute("SELECT * FROM exam_schedule WHERE dept=%s OR dept='All' ORDER BY exam_date ASC", (dept,))
            rows = cur.fetchall()
            for r in rows:
                if r.get('exam_date'): r['exam_date'] = str(r['exam_date'])
                if r.get('created_at'): r['created_at'] = str(r['created_at'])
            return jsonify(rows)
    finally: con.close()

@app.route('/api/exam_schedule', methods=['POST'])
def add_exam_schedule():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO exam_schedule (subject,exam_date,start_time,end_time,hall,total_marks,dept,year_str,section,posted_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (d.get('subject'), d.get('exam_date'), d.get('start_time',''), d.get('end_time',''), d.get('hall',''), d.get('total_marks',100), d.get('dept','All'), d.get('year_str','All'), d.get('section','All'), d.get('posted_by','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/api/exam_schedule/<int:eid>', methods=['DELETE'])
def del_exam_schedule(eid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM exam_schedule WHERE id=%s", (eid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── NOTIFICATIONS ────────────────────────────────────────────────────
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    con = get_db()
    try:
        with con.cursor() as cur:
            dept = request.args.get('dept','')
            cur.execute("SELECT * FROM notifications WHERE dept=%s OR dept='All' ORDER BY created_at DESC LIMIT 50", (dept,))
            rows = cur.fetchall()
            for r in rows:
                if r.get('created_at'): r['created_at'] = str(r['created_at'])
            return jsonify(rows)
    finally: con.close()

@app.route('/api/notifications', methods=['POST'])
def add_notification():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO notifications (title,message,type,dept,year_str,posted_by) VALUES (%s,%s,%s,%s,%s,%s)",
                (d.get('title'), d.get('message',''), d.get('type','info'), d.get('dept','All'), d.get('year_str','All'), d.get('posted_by','')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/notifications/<int:nid>', methods=['DELETE'])
def del_notification(nid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM notifications WHERE id=%s", (nid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

# ── SUBMISSIONS ──────────────────────────────────────────────────────
@app.route('/api/submissions', methods=['POST'])
def submit_assignment():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO submissions (assignment_id,student_id,student_name,file_name,file_data) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE file_name=%s,file_data=%s",
                (d.get('assignment_id'), d.get('student_id'), d.get('student_name',''), d.get('file_name',''), d.get('file_data',''), d.get('file_name',''), d.get('file_data','')))
            con.commit()
            return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/api/submissions/<int:sid>/download')
def download_submission(sid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM submissions WHERE id=%s", (sid,))
            row = cur.fetchone()
        if not row: return jsonify({'ok': False}), 404
        return jsonify({'ok': True, 'file_name': row['file_name'], 'file_data': row['file_data']})
    finally: con.close()

@app.route('/api/faculty/<int:fid>', methods=['PUT'])
def update_faculty(fid):
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            fields, vals = [], []
            for k in ['name','nm','username','un','password','pw','role','dept','department','phone','ph','exp']:
                if k in d:
                    col = {'nm':'name','un':'username','pw':'password','ph':'phone','dept':'dept','department':'dept','exp':'experience'}.get(k,k)
                    fields.append(f"{col}=%s")
                    vals.append(d[k])
            if not fields: return jsonify({'ok':False,'msg':'Nothing to update'})
            vals.append(fid)
            cur.execute(f"UPDATE faculty SET {','.join(fields)} WHERE id=%s", vals)
            con.commit()
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/api/students/<int:sid>', methods=['PUT'])
def update_student(sid):
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            fields, vals = [], []
            for k in ['name','nm','username','un','password','pw','reg_no','reg','year','yr','section','sec','dept','department','email','em','phone','ph']:
                if k in d:
                    col = {'nm':'name','un':'username','pw':'password','reg':'reg_no','yr':'year','sec':'section','ph':'phone','dept':'dept','department':'dept','em':'email'}.get(k,k)
                    fields.append(f"{col}=%s")
                    vals.append(d[k])
            if not fields: return jsonify({'ok':False,'msg':'Nothing to update'})
            vals.append(sid)
            cur.execute(f"UPDATE students SET {','.join(fields)} WHERE id=%s", vals)
            con.commit()
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

@app.route('/api/exam_timetables', methods=['GET'])
def get_exam_timetables():
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id,label,sem_name,semester,year,dept,image FROM exam_timetables ORDER BY created_at DESC")
            rows = cur.fetchall()
        return jsonify(rows)
    finally: con.close()

@app.route('/api/exam_timetables', methods=['POST'])
def add_exam_timetable():
    try:
        d = request.json
        if not d:
            return jsonify({'ok': False, 'msg': 'No data received'})
        label = d.get('label','')
        sem_name = d.get('sem_name','')
        semester = d.get('semester','')
        year = d.get('year','')
        dept = d.get('dept','')
        image = d.get('image','')
        if not label:
            return jsonify({'ok': False, 'msg': 'Label required'})
        con = get_db()
        try:
            with con.cursor() as cur:
                cur.execute("INSERT INTO exam_timetables (label,sem_name,semester,year,dept,image) VALUES (%s,%s,%s,%s,%s,%s)",
                    (label, sem_name, semester, year, dept, image))
                con.commit()
                new_id = cur.lastrowid
            return jsonify({'ok': True, 'id': new_id})
        except Exception as ex:
            return jsonify({'ok': False, 'msg': 'DB error: '+str(ex)})
        finally:
            con.close()
    except Exception as ex:
        return jsonify({'ok': False, 'msg': 'Server error: '+str(ex)})

@app.route('/api/exam_timetables/<int:tid>', methods=['DELETE'])
def del_exam_timetable(tid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM exam_timetables WHERE id=%s", (tid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()


# ── PASSWORD CHANGE ─────────────────────────────────────────────
@app.route('/api/student/change-password', methods=['POST'])
def student_change_password():
    d = request.json
    if 'student' not in session:
        return jsonify({'ok': False, 'msg': 'Not logged in'}), 401
    con = get_db()
    try:
        with con.cursor() as cur:
            sid = session['student']['id']
            cur.execute("SELECT password FROM students WHERE id=%s", (sid,))
            row = cur.fetchone()
            if not row or row['password'] != d.get('old_password',''):
                return jsonify({'ok': False, 'msg': 'Current password incorrect'})
            new_un = d.get('new_username','').strip()
            new_pw = d.get('new_password','').strip()
            if new_un:
                cur.execute("UPDATE students SET username=%s WHERE id=%s", (new_un, sid))
                session['student']['username'] = new_un
            if new_pw:
                cur.execute("UPDATE students SET password=%s WHERE id=%s", (new_pw, sid))
            con.commit()
        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'ok': False, 'msg': str(ex)}), 200
    finally: con.close()

# ── CIRCULARS ───────────────────────────────────────────────────
@app.route('/api/circulars', methods=['GET'])
def get_circulars():
    con = get_db()
    try:
        with con.cursor() as cur:
            dept = request.args.get('dept','')
            if dept:
                cur.execute("SELECT id,title,dept,file_name,posted_by,created_at FROM circulars WHERE dept=%s OR dept='All' ORDER BY created_at DESC", (dept,))
            else:
                cur.execute("SELECT id,title,dept,file_name,posted_by,created_at FROM circulars ORDER BY created_at DESC")
            rows = cur.fetchall()
        for r in rows:
            if r.get('created_at'): r['created_at'] = str(r['created_at'])
        return jsonify(rows)
    finally: con.close()

@app.route('/api/circulars', methods=['POST'])
def add_circular():
    d = request.json
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO circulars (title,dept,file_name,file_data,posted_by) VALUES (%s,%s,%s,%s,%s)",
                (d['title'], d.get('dept','All'), d.get('file_name',''), d.get('file_data',''), d.get('posted_by','Admin')))
            con.commit()
            return jsonify({'ok': True, 'id': cur.lastrowid})
    finally: con.close()

@app.route('/api/circulars/<int:cid>', methods=['GET'])
def get_circular_file(cid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT file_data,file_name FROM circulars WHERE id=%s", (cid,))
            row = cur.fetchone()
        if not row or not row['file_data']:
            return jsonify({'ok': False}), 404
        return jsonify({'ok': True, 'file_data': row['file_data'], 'file_name': row['file_name']})
    finally: con.close()

@app.route('/api/circulars/<int:cid>', methods=['DELETE'])
def del_circular(cid):
    con = get_db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM circulars WHERE id=%s", (cid,))
            con.commit()
        return jsonify({'ok': True})
    finally: con.close()

if __name__ == '__main__':
    app.run(debug=True)
