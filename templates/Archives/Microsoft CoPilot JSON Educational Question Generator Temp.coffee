JSON Educational Question Generator Template

REQUIREMENTS

Please generate educational questions in JSON format following these guidelines:

1. Output valid JSON only, starting with { and ending with }
2. Use LaTeX notation for all mathematical content
3. Follow the exact structure specified below
4. Do not include citations or reference markers

MATHEMATICAL NOTATION

Use LaTeX delimiters for all mathematical content:
    Variables: $V$, $I$, $R$, $f$, $\omega$, $\pi$
    Units: $10\,\Omega$, $5\,\text{V}$, $1\,\text{kHz}$, $100\,\text{mA}$
    Equations: $I = V/R$, $P = I^2R$, $Z = R + j\omega L$
    Greek letters: $\omega$, $\pi$, $\Omega$, $\mu$, $\alpha$, $\beta$
    Subscripts/Superscripts: $V_{rms}$, $I_{max}$, $x^2$, $f_0$

Avoid Unicode symbols in JSON. Use LaTeX equivalents instead.

EDUCATIONAL QUALITY

Create high-quality educational content:
    Keep question text clear and focused
    Match difficulty to learning objectives
    Use realistic values from industry practice
    Create plausible distractors for multiple choice
    Provide meaningful explanations in feedback
    Show calculations with proper LaTeX formatting

REQUIRED JSON STRUCTURE

Your response must use this exact structure:

{
  "questions": [
    {
      "type": "multiple_choice",
      "title": "Descriptive title",
      "question_text": "Question with LaTeX math $V = IR$",
      "choices": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Exact correct option text",
      "points": 1,
      "tolerance": 0.05,
      "feedback_correct": "Explanation with calculations",
      "feedback_incorrect": "Hint for learning",
      "image_file": [],
      "topic": "Main topic area",
      "subtopic": "Specific concept",
      "difficulty": "Easy"
    },
    {
      "type": "numerical",
      "title": "Calculation problem",
      "question_text": "Calculate $I$ when $V = 12\,\text{V}$ and $R = 4\,\Omega$",
      "choices": [],
      "correct_answer": "3",
      "points": 2,
      "tolerance": 0.1,
      "feedback_correct": "Correct! $I = V/R = 12/4 = 3\,\text{A}$",
      "feedback_incorrect": "Use Ohm's law: $I = V/R$",
      "image_file": [],
      "topic": "Circuit Analysis",
      "subtopic": "Ohm's Law",
      "difficulty": "Easy"
    }
  ]
}

SUPPORTED QUESTION TYPES

multiple_choice: 4 options, one correct answer
numerical: Numeric answer with tolerance
true_false: Boolean question with True/False choices


OUTPUT INSTRUCTIONS

Please provide only the JSON response starting with {"questions":[ and ending with ]}

No explanatory text before or after the JSON is needed.
```