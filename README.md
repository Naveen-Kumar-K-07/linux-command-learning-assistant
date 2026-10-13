# Linux Commands Learning Assistant — Full-Stack Web Application

A full-stack web application designed to teach Linux command-line operations, shell scripting, and systems administration through **interactive terminal simulation**, **live virtual filesystem visualizers**, **step-by-step telemetry**, **topic assessments**, and **verifiable PDF certifications**.

---

## 🌟 Key Features

1. **Terminal-Inspired Developer UI/UX**
   - Sleek dark theme (JetBrains Mono & Inter typography, terminal greens, cyan highlights, obsidian slate backgrounds, glowing badges).
   - Fully responsive for mobile, tablet, and desktop.

2. **Secure Authentication & Gmail Registration**
   - User registration with Full Name, Gmail address (`@gmail.com`), password hashing (`Werkzeug`), and confirmation checks.
   - Duplicate email prevention and parameterized database storage.
   - Email verification token and 6-digit code support (via Gmail SMTP with development fallback mode).
   - Secure session management with Flask-Login.

3. **Dashboard with Exactly Four Main Navigation Modules**
   - **Learn**: Comprehensive curriculum spanning 30+ core Linux commands across 11 categories and 3 difficulty levels.
   - **Assessment**: Topic-wise and level-wise quizzes with multiple-choice, syntax, and scenario questions.
   - **Certification**: Automated eligibility checking and high-resolution downloadable PDF certificate generation.
   - **Logout**: Secure session termination preserving all account data and progress in MySQL.

4. **Interactive Linux Terminal Simulator & Live Filesystem Visualizer**
   - **Safe Sandbox Execution**: Controlled command interpreter operating completely inside a virtual filesystem (VFS) without executing arbitrary host OS processes (`os.system` / `subprocess`).
   - **Real Virtual State**: Commands modify an in-memory & database-persisted filesystem tree (`mkdir`, `touch`, `rm`, `rm -r`, `cp`, `mv`, `cat`, `echo "text" > file`, `echo "text" >> file`, `ls`, `ls -la`, `pwd`, `cd`, `grep`, `head`, `tail`, `wc`, `chmod`, `whoami`, `uname`, `date`, `df`, `free`, `ps`, `top`, `kill`, `ping`, `curl`, `ifconfig`, `apt`, `clear`, pipes `|`, and output redirects).
   - **Live Filesystem Inspector**: Real-time hierarchical file tree visualizer displaying directory entries, sizes, and permissions (`drwxr-xr-x`, `-rw-r--r--`).
   - **Step-by-Step Breakdown**: Clear educational explanation and telemetry after every executed command.
   - **Interactive Practice Tasks**: Built-in challenges validated in real-time as users run commands in the terminal.

5. **Persistent Learning Progress**
   - Every completed lesson, practice task, and terminal state is saved to MySQL per authenticated user ID.
   - **Continue Learning**: Automatically resumes at the exact lesson and position where the user previously stopped.
   - Full data isolation between different accounts.

6. **Tamper-Proof Certification Module**
   - Requires fulfilling configured completion requirements (at least 80% curriculum completion and passing a practical assessment).
   - Server-side verification before issuance prevents manual API spoofing.
   - Generates vector PDF certificates using **ReportLab** with unique Certificate ID (e.g., `LCLA-2026-X8F9A2B`), cryptographic verification hash, issue date, and recipient name.
   - Public verification endpoint at `/verify-certificate/<cert_id>`.

---

## 🏗️ Technology Stack

- **Frontend**: HTML5, CSS3 (Vanilla modern dark design system), JavaScript (ES6+ terminal engine & VFS tree visualizer), Font Awesome 6.5.
- **Backend**: Python 3.10+ using the **Flask** framework.
- **Database**: **MySQL** (via `Flask-SQLAlchemy` & `PyMySQL`). Supports seamless out-of-the-box local testing with fallback SQLite if MySQL server is not locally running.
- **Authentication**: `Flask-Login` and `Werkzeug` security password hashing.
- **Certificate Generation**: `ReportLab` vector PDF generator.
- **Validation & Email**: `email-validator` and `smtplib` for Gmail TLS verification.

---

## 📁 Project Structure

```
USP Project/
├── app.py                      # Application entry point and Flask factory
├── config.py                   # Environment configuration (MySQL / fallback SQLite)
├── requirements.txt            # Python package dependencies
├── .env.example                # Sample environment variables
├── .env                        # Local active configuration
├── models/
│   ├── __init__.py             # Database instance and exports
│   ├── user.py                 # User model (auth, password hash, email verified)
│   ├── lesson.py               # Lesson model (syntax, explanation, examples, tasks)
│   ├── progress.py             # UserProgress and UserLearningState models
│   ├── terminal.py             # TerminalState model (persistent VFS JSON)
│   ├── assessment.py           # Quizzes, questions, and attempts models
│   └── certificate.py          # Certificate model (unique ID, verification hash)
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Registration, verification, login, logout
│   ├── dashboard.py            # Exactly 4 main navigation modules + user stats
│   ├── learn.py                # Lesson browsing, detail, progress tracking
│   ├── terminal.py             # Sandbox execution API & VFS state sync
│   ├── assessment.py           # Quizzes, tests, scoring, attempt history
│   └── certificate.py          # Eligibility validation & PDF download
├── services/
│   ├── __init__.py
│   ├── simulator.py            # Controlled virtual Linux command sandbox (VFS)
│   ├── pdf_generator.py        # ReportLab vector PDF certificate engine
│   ├── progress_service.py     # Progress calculation and resume markers
│   └── email_service.py        # Gmail verification dispatcher & dev mode helper
├── database/
│   ├── schema.sql              # Normalized MySQL database schema
│   ├── seed_data.py            # Curriculum seeder (30 lessons + 3 exams)
│   └── setup_mysql.py          # Standalone MySQL initialization script
├── templates/
│   ├── base.html               # Main layout with responsive navbar & alerts
│   ├── landing.html            # Landing page with hero & terminal animation
│   ├── auth/                   # Login, register, verify, forgot-password
│   ├── dashboard.html          # Dashboard with 4 main navigation cards
│   ├── learn/                  # Curriculum index and interactive dual-pane lesson
│   ├── assessment/             # Quiz list, interactive test, and answer review
│   ├── certificate/            # Eligibility dashboard and public verification
│   └── errors/                 # 404 and 500 error handlers
├── static/
│   ├── css/
│   │   ├── style.css           # Primary developer dark stylesheet
│   │   └── terminal.css        # Interactive terminal and VFS inspector styles
│   └── js/
│       ├── main.js             # Alert dismissals and general UI
│       └── terminal.js         # Command history, execution sync, and tree visualizer
└── tests/
    └── test_app.py             # Full unit and integration test suite (14 tests)
```

---

## 🚀 Getting Started Locally (Windows / VS Code)

### 1. Prerequisites
- **Python 3.10+** installed on Windows.
- Optional: **MySQL Server 8.0+** or **XAMPP** (if using MySQL; if MySQL is not running, the application automatically uses a local SQLite database for instant development).

### 2. Clone or Open in VS Code
Open this folder in VS Code:
```powershell
code "c:\Users\navee\OneDrive\Desktop\USP Project"
```

### 3. Install Dependencies
Open a PowerShell terminal in VS Code and run:
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` or edit `.env`:
```powershell
Copy-Item .env.example .env
```
Default `.env` settings:
```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=linux-assistant-dev-secret-key-2026-secure-session
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=linux_learning_assistant
DEV_MODE_AUTO_VERIFY=True
```

### 5. (Optional) Initialize MySQL Database
If you have MySQL Server installed and running:
```powershell
python database/setup_mysql.py
```
This automatically executes `schema.sql`, creates the `linux_learning_assistant` database, and populates all 30 lessons and quizzes!

### 6. Run the Application
Start the Flask development server:
```powershell
python app.py
```
Output:
```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running the Automated Test Suite

To run all 14 unit and integration tests:
```powershell
python -m unittest tests/test_app.py -v
```
All tests verify:
- New user registration and password hashing.
- Duplicate email rejection.
- Login, session persistence, and secure logout.
- User-specific learning progress isolation.
- Virtual Linux simulator command execution (`pwd`, `ls`, `mkdir`, `touch`, `cp`, `rm`, `cat`, `echo`, `grep`, `chmod`).
- Assessment scoring and attempt history.
- Certificate eligibility and PDF generation.

---

## 📜 Supported Terminal Simulator Commands

The simulator executes inside an isolated virtual filesystem:
- **Navigation**: `pwd`, `ls`, `ls -l`, `ls -a`, `ls -la`, `cd <path>`, `cd ..`, `cd ~`, `cd /`
- **File Management**: `mkdir`, `mkdir -p`, `touch`, `cp`, `cp -r`, `mv`, `rm`, `rm -r`, `rmdir`
- **File Viewing**: `cat`, `head -n <N>`, `tail -n <N>`
- **Text Search & Count**: `grep`, `grep -i`, `find <path> -name <pattern>`, `wc`, `wc -l`
- **Permissions**: `chmod <mode>` (octal `755`, `644`, or `+x`), `chown`
- **Processes**: `ps`, `ps aux`, `top`, `kill <PID>`
- **System Info**: `uname`, `uname -a`, `whoami`, `id`, `date`, `df -h`, `du`, `free -m`
- **Networking**: `ping -c <N> <host>`, `curl <URL>`, `ifconfig`, `ip a`, `netstat`
- **Packages**: `apt update`, `apt install <pkg>`, `dpkg`
- **Shell & Pipes**: `echo <text>`, `echo "text" > file`, `echo "text" >> file`, command piping `|`, `clear`, `history`, `help`

---

## 🔒 Security Measures

- **No Arbitrary Code Execution**: The simulator parses user input in Python and manipulates an in-memory VFS dictionary; it never invokes `os.system()` or `subprocess.Popen()` with user input.
- **Password Protection**: Passwords are saved exclusively as salted hashes via Werkzeug (`generate_password_hash`).
- **Authorization**: All progress, attempts, and certificate routes check `current_user.id` to prevent cross-account tampering.
- **Backend Eligibility**: Certificates cannot be generated by altering frontend state or sending spoofed requests; all requirements are verified server-side.

---

## 📄 License
Created for Linux Commands Learning Assistant — Full-Stack Educational Web Platform.
