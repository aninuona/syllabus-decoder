# Syllabus Decoder - Complete README

A web application that helps teachers and students understand and create clear AI policies for college courses.

**Live Application**: https://syllabus-decoder.onrender.com

## What is Syllabus Decoder

Syllabus Decoder is a website that helps people understand what teachers' AI policies actually mean. When a student reads "generative AI may be used for brainstorming with proper documentation," the boundaries and relative strictness may be unclear. Syllabus Decoder translates this into a simple code: T3 C2 E1.

Think of it like a translator for AI policies. Just like you might use Google Translate to understand Spanish, you can use Syllabus Decoder to understand what your teacher's AI policy means.

## Why Does This Exist

When ChatGPT became popular in late 2022, teachers suddenly had to decide how students could use it. But everyone wrote their policies differently. Some teachers said no AI at all. Others said AI was fine. Most were somewhere in between.

Students got confused. They didn't know:
- Can I use ChatGPT for this assignment?
- If I use AI, does my teacher need to know?
- What happens if I use AI when I'm not supposed to?
- Why does the other professor teaching this course allow AI, but mine doesn't?

Syllabus Decoder creates a standard way to talk about AI policies. Instead of guessing what your teacher meant, you can get a clear classification.

## What Can You Do With It

### 1. Understand Your Teacher's Policy (Decoder Tool)

Paste your teacher's AI policy text. Get back: T3 C2 E1 (or whatever applies)

- T Tier tells you how much AI is allowed (T0 = banned, T5 = encouraged)
- C Level tells you if you need to document it (C0 = no documentation, C3 = full logs)
- E Level tells you what happens if you break the rules (E0 = nothing, E3 = extreme consequence e.g. failure)

### 2. Create Your Own Policy (Policy Builder)

Teachers answer 3 questions. The system generates ready-to-use policy text.

Questions are simple like:
- Is AI helpful or not helpful?
- How much do you care about the details of usage?
- What are your views on punishment?

Copy and paste the generated text into your syllabus.

### 3. Learn About Policies (Training Game)

Anyone can practice classifying policies. The game shows you real syllabus quotes and asks you to guess their classification. You get instant feedback.

Great for students learning about AI policies and teachers improving their policy writing. 

### 4. Manage a Database (Admin Console)

Administrators can:
- Add new policies from different schools
- Edit and verify policies
- Search and filter
- Export data for research

## Before You Install

### What You Need

1. **Python 3.8 or newer**
   - Check: `python --version`
   - Download: https://www.python.org/downloads/
   - Remember to check "Add to PATH" during installation

2. **Git** (optional but recommended)
   - Download: https://git-scm.com/

3. **A text editor**
   - VS Code: https://code.visualstudio.com/
   - Or any basic text editor

4. **A web browser**
   - Chrome, Firefox, Safari, or Edge

5. **Hard drive space**
   - 500 MB minimum for development
   - 10 GB for production

6. **RAM**
   - 1-2 GB for development
   - 4+ GB for production

## Installation (For Your Computer)

### Step 1: Get the Code

```bash
git clone https://github.com/aninuona/syllabus-decoder.git
cd syllabus-decoder
```

Or download the ZIP from GitHub and unzip it.

### Step 2: Create Virtual Environment

Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Packages

```bash
pip install -r requirements.txt
```

This installs everything Syllabus Decoder needs.

### Step 4: Set Up Database

```bash
python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

### Step 5: Load Sample Data

```bash
python seed_builder_questions.py
python seed_syllabus_entries.py
```

### Step 6: Create Admin Account

```bash
python create_admin.py
```

Type your email when asked.

## Running Locally

In the syllabus-decoder folder with virtual environment activated:

```bash
python app.py
```

Then open: http://localhost:5000

You're now running Syllabus Decoder locally.

## Deploying to Production

For real users on the internet, you need a production server.

### Our Deployment: Render

Syllabus Decoder is currently deployed on **Render**, a modern cloud platform that's easy to use and affordable.

**Live URL**: https://syllabus-decoder.onrender.com

**Why Render?**
- Simple deployment from GitHub
- Built-in PostgreSQL database
- Automatic SSL/HTTPS
- Free or $7-12/month starting price
- Excellent uptime
- Easy scaling as traffic grows

### How We Deployed to Render

If you want to deploy YOUR version to Render, follow these steps:

**Step 1: Prepare Your Code**

Create a file called `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: syllabus-decoder
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: FLASK_ENV
        value: production
```

Also create a `Procfile`:
```
web: gunicorn app:app
```

**Step 2: Push to GitHub**

Make sure your code is on GitHub:

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

**Step 3: Create Render Account**

1. Go to https://render.com
2. Sign up (free account)
3. Connect your GitHub account

**Step 4: Create New Service**

1. Click "New Web Service"
2. Select your syllabus-decoder repository
3. Set name to "syllabus-decoder"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Click "Create Web Service"

**Step 5: Add Environment Variables**

In Render dashboard, go to Environment:

```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here-at-least-32-characters
DATABASE_URL=postgresql://... (Render provides this automatically)
ADMIN_EMAIL=admin@yourinstitution.edu
```

To generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Step 6: Add PostgreSQL Database**

1. In Render dashboard, click "New"
2. Select "PostgreSQL"
3. Name it "syllabus-decoder-db"
4. Note the connection string
5. Render automatically sets DATABASE_URL

**Step 7: Deploy**

Render automatically deploys when you push to GitHub.

**Step 8: Initialize Database**

After deploy completes, run in Render shell:

```bash
python -c "from app import create_app, db; app = create_app(); db.create_all()"
python seed_builder_questions.py
python seed_syllabus_entries.py
python create_admin.py
```

The app is now live at: https://your-app-name.onrender.com

### Using Your Own Domain with Render

After deploying to Render:

1. Buy a domain (e.g., syllabusdecoder.yourinstitution.edu)
2. In Render dashboard, go to Settings
3. Find "Custom Domain"
4. Enter your domain
5. Follow Render's instructions for DNS settings
6. Wait 24-48 hours for changes to take effect

### Alternative Deployment Options

While we use Render, you could also deploy to:

**Heroku** (Similar to Render)
- https://www.heroku.com
- Pros: Very easy, lots of documentation
- Cons: $7+/month

**DigitalOcean** (More control, cheaper)
- https://www.digitalocean.com
- Pros: Cheaper ($4-12/month), more control
- Cons: Requires more Linux knowledge

**Railway** (Like Render but different pricing)
- https://railway.app
- Pros: Simple deployment, pay-as-you-go
- Cons: Costs vary more unpredictably

**Your Institution's Servers** (Free)
- Talk to your IT department
- Pros: Free, secure
- Cons: Slow IT approval process


## Understanding the Classification System

### T Tier (How Much AI is Allowed)

- **T0**: AI is completely prohibited. No ChatGPT, no exceptions.
- **T1**: AI is mostly not allowed. Only in very specific situations the teacher approves.
- **T2**: You have to ask permission first. Teacher decides case-by-case.
- **T3**: AI is OK for certain tasks. Like brainstorming or outlining, but not writing final drafts.
- **T4**: AI is allowed if you document it. You can use it but must say so.
- **T5**: AI is encouraged. Teacher wants you to use it and learn from it.

### C Level (Documentation Requirements)

- **C0**: Nothing required. Your teacher doesn't care if you mention it.
- **C1**: Just mention it. A quick note that you used AI.
- **C2**: Formal citation. Like citing a source: "ChatGPT, 2024."
- **C3**: Full logs. Show exactly what prompts you used and what AI wrote.

### E Level (Consequences)

- **E0**: Trust-based. Your teacher trusts you won't cheat.
- **E1**: Warnings. Teacher explains the risks if you cheat.
- **E2**: Active checking. Teacher will use AI detectors or check your work.
- **E3**: Zero tolerance. Using AI when forbidden = automatic consequences such as reporting or failure.

### Examples

**Example 1**: T3 C1 E1
Means: AI allowed for specific tasks, just mention it if you use it, teacher warned about risks.

**Example 2**: T0 C0 E3
Means: No AI allowed at all, if caught it's automatic expulsion.

**Example 3**: T5 C0 E0
Means: Use AI freely, document it or not, no punishment (teacher trusts you).

## How the System Classifies Policies

The Decoder uses a technique called TF-IDF. It's like a smart detector that looks for keywords.

For example:
- If it sees "prohibited," "banned," "not allowed" = T0
- If it sees "brainstorm," "outline," "limited" = T3
- If it sees "encouraged," "freely" = T5

The system is about 78% accurate. It works best for very permissive or very restrictive policies. Middle-ground policies are harder because they're often written ambiguously. 

## Project Structure

```
syllabus-decoder/
├── app.py                        # Main application
├── models.py                     # Database tables
├── auth.py                       # Login system
├── decoder.py                    # Classification logic
├── builder.py                    # Policy generation
├── game.py                       # Training game
├── admin.py                      # Admin features
├── requirements.txt              # Dependencies
├── create_admin.py               # Create admin accounts
├── seed_builder_questions.py     # Load questions
├── seed_syllabus_entries.py      # Load sample policies
├── Procfile                      # For Render deployment
├── render.yaml                   # Render configuration
├── templates/                    # Web pages (HTML)
│   ├── index.html               # Home page
│   ├── decoder.html             # Decoder page
│   ├── build_syllabus.html      # Policy Builder
│   ├── training_game.html       # Training Game
│   ├── admin.html               # Admin Console
│   └── login.html               # Login page
└── static/                      # Styling and images
    └── style.css                # CSS
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

Forgot to activate virtual environment or didn't install packages.

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Address already in use"

Port 5000 is being used by something else.

```bash
python app.py --port 5001
```

### "No such file or directory: 'syllabus.csv'"

You're in the wrong folder. Make sure you're in syllabus-decoder.

```bash
ls  (Mac/Linux)
dir (Windows)
```

### Can't login to admin

Email wasn't authorized. Run:
```bash
python create_admin.py
```

Use the exact same email.

### Deployed app shows blank page

Check logs on Render dashboard. Look for error messages. Common fixes:

1. Make sure DATABASE_URL is set: In Render settings, verify PostgreSQL connection
2. Make sure SECRET_KEY is set: In Render settings, check environment variables
3. Restart the service: In Render dashboard, click "Restart latest deployment"
4. Check that database tables exist: Run initialization commands again

## Contributing

### Share Policies

Want to upload your own policy? Share it!

1. Go to GitHub: https://github.com/aninuona/syllabus-decoder
2. Click "Issues"
3. Click "New Issue"
4. Paste the policy text and include the institution name and course discipline

### Report Bugs

Found something broken?

1. Click "Issues" on GitHub
2. "New Issue"
3. Describe what went wrong and how to reproduce it

### Suggest Features

Have an idea?

1. GitHub Issues
2. "New Issue"
3. Describe your idea

### Improve Code

Want to help?

1. Fork the repository
2. Make changes in a new branch
3. Submit a pull request
4. Explain what you changed and why

## Support

### Getting Help

**Bug Reports**: https://github.com/aninuona/syllabus-decoder/issues

**Security Issues**: Email the maintainer privately (don't post on GitHub)

## FAQ

**Q: Can I use this at my school?**
A: Yes! It's free and open source. Deploy it to Render, Heroku, or your own servers.

**Q: How much does it cost?**
A: Free software. Render deployment costs $7-12/month (or free tier has limitations).

**Q: Is it mobile-friendly?**
A: Yes, works great on phones and tablets.

**Q: Can I change it?**
A: Yes, the code is open for customization.

**Q: What if I don't know programming?**
A: You can still use it. Just follow the setup instructions.

**Q: How accurate is the classifier?**
A: About 78% on real policies. Works best for extreme policies (T0 or T5).

**Q: Can students see other schools' policies?**
A: Yes, the app shows a database of anonymized policies. Good for research.

**Q: Is data secure?**
A: Passwords are encrypted. Use HTTPS in production (Render provides this). Don't store sensitive info.

**Q: Why Render instead of Heroku?**
A: Render is easier to use, has a free tier for testing, includes PostgreSQL database, and is cheaper overall.

## Future Plans

- Feedback options
- Canvas/Blackboard integration
- Improved AI classifier
- Advanced data visualization
- Public database

## License

Open

## Version

Version 1.0 - May 2026

## Thank You

Thanks for using Syllabus Decoder. Please share it with colleagues!

Try the live app: https://syllabus-decoder.onrender.com

Questions? Email abokka@oldwestbury.edu

GitHub: https://github.com/aninuona/syllabus-decoder
