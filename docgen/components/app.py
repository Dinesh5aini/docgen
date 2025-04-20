from flask import Flask, render_template, request, redirect, url_for
from modules.gemini_api import generate_report_sections

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form['topic']
    context = request.form['context']

    # Generate section-wise content
    sections = generate_report_sections(topic, context)

    return render_template('report_editor.html', topic=topic, sections=sections)

@app.route('/preview', methods=['POST'])
def preview():
    # Collect edited sections
    sections = request.form.to_dict()
    return render_template('generated_report.html', sections=sections)

if __name__ == '__main__':
    app.run(debug=True)