import { useState } from "react";
import { CheckCircle, AlertTriangle } from "lucide-react";
import { useApp } from "../state/AppContext.tsx";
import { completeTraining } from "../api/index.ts";

interface Scenario {
  id: number;
  question: string;
  options: { value: string; label: string }[];
  correctAnswer: string;
  explanation: string;
}

const SCENARIOS: Scenario[] = [
  {
    id: 1,
    question:
      "A colleague asks you to paste their SSN into an AI assistant to generate a tax summary. What should you do?",
    options: [
      {
        value: "a",
        label: "Paste the SSN directly — the AI tool is internal",
      },
      {
        value: "b",
        label: "Replace the SSN with a placeholder like [SSN] before submitting",
      },
      {
        value: "c",
        label: "Report the request to your manager first",
      },
    ],
    correctAnswer: "b",
    explanation:
      "Always replace personally identifiable information (PII) such as SSNs with placeholders before sending to any AI tool. PromptGuard does this automatically, but it's important to understand the principle. Even internal AI tools may log prompts or use them for training.",
  },
  {
    id: 2,
    question:
      'You need to debug an API integration. Your prompt includes "api_key=sk-live-abc123xyz". What\'s the safest approach?',
    options: [
      {
        value: "a",
        label: "Send it as-is — it's a development key",
      },
      {
        value: "b",
        label: "Replace the key with a dummy value like [API_KEY] and describe the issue generically",
      },
      {
        value: "c",
        label: "Delete the key and just ask the AI to guess the issue",
      },
    ],
    correctAnswer: "b",
    explanation:
      "API keys and tokens must never be shared in AI prompts, even in development environments. Replace credentials with placeholders and describe the problem without exposing secrets. PromptGuard detects credentials automatically, but developing this habit ensures safety across all tools.",
  },
  {
    id: 3,
    question:
      'You\'re drafting an email with the AI tool and PromptGuard flags your message as containing "Internal" content. What should you do?',
    options: [
      {
        value: "a",
        label: "Override PromptGuard and send anyway",
      },
      {
        value: "b",
        label: "Review the safer rewrite suggested by PromptGuard and use it if appropriate",
      },
      {
        value: "c",
        label: "Stop using the AI tool for this task entirely",
      },
    ],
    correctAnswer: "b",
    explanation:
      "When PromptGuard flags content, review the suggested safer rewrite. It typically replaces internal or confidential references with safe placeholders while keeping the intent of your message. You can edit the rewrite if needed. Completely avoiding AI tools isn't necessary — just use them safely.",
  },
];

export default function TrainingPage() {
  const { setUserRisk, userRisk } = useApp();
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [completed, setCompleted] = useState(userRisk.trainingCompleted);

  const allAnswered = SCENARIOS.every((s) => answers[s.id]);
  const allCorrect =
    submitted && SCENARIOS.every((s) => answers[s.id] === s.correctAnswer);

  const handleSubmit = () => {
    setSubmitted(true);
    if (SCENARIOS.every((s) => answers[s.id] === s.correctAnswer)) {
      completeTraining();
      setUserRisk({
        ...userRisk,
        trainingCompleted: true,
        trainingRequired: false,
      });
      setCompleted(true);
    }
  };

  return (
    <main className="flex-1 overflow-y-auto p-6" id="main-content">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-gray-900">
            Security Awareness Training
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Complete this micro-training to reinforce AI safety best practices.
          </p>
        </div>

        {completed && (
          <div
            className="mb-6 flex items-center gap-3 bg-emerald-50 border border-emerald-200 rounded-2xl p-4"
            role="status"
            aria-live="polite"
          >
            <CheckCircle
              className="w-5 h-5 text-emerald-600 flex-shrink-0"
              aria-hidden="true"
            />
            <div>
              <p className="text-sm font-semibold text-emerald-800">
                Training completed
              </p>
              <p className="text-xs text-emerald-600">
                Your risk status has been updated. Keep applying these
                principles in your daily work.
              </p>
            </div>
          </div>
        )}

        <div className="space-y-6">
          {SCENARIOS.map((scenario) => {
            const userAnswer = answers[scenario.id];
            const isCorrect = userAnswer === scenario.correctAnswer;
            const showResult = submitted;

            return (
              <section
                key={scenario.id}
                className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm"
              >
                <h2 className="text-sm font-semibold text-gray-900 mb-4">
                  Scenario {scenario.id}
                </h2>
                <p className="text-sm text-gray-700 mb-4 leading-relaxed">
                  {scenario.question}
                </p>

                <fieldset>
                  <legend className="sr-only">
                    Answer options for scenario {scenario.id}
                  </legend>
                  <div className="space-y-2">
                    {scenario.options.map((opt) => {
                      const isSelected = userAnswer === opt.value;
                      const isThisCorrect =
                        opt.value === scenario.correctAnswer;
                      let ringClass = "border-gray-200";
                      if (showResult && isSelected && isCorrect) {
                        ringClass = "border-emerald-400 bg-emerald-50";
                      } else if (showResult && isSelected && !isCorrect) {
                        ringClass = "border-red-400 bg-red-50";
                      } else if (showResult && isThisCorrect) {
                        ringClass = "border-emerald-300 bg-emerald-50";
                      }

                      return (
                        <label
                          key={opt.value}
                          className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-colors hover:bg-gray-50 ${ringClass}`}
                        >
                          <input
                            type="radio"
                            name={`scenario-${scenario.id}`}
                            value={opt.value}
                            checked={isSelected}
                            onChange={() => {
                              if (!submitted) {
                                setAnswers((prev) => ({
                                  ...prev,
                                  [scenario.id]: opt.value,
                                }));
                              }
                            }}
                            disabled={submitted}
                            className="mt-0.5 accent-brand-red"
                          />
                          <span className="text-sm text-gray-700">
                            {opt.label}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                </fieldset>

                {showResult && (
                  <div
                    className={`mt-4 p-3 rounded-xl text-sm leading-relaxed ${
                      isCorrect
                        ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                        : "bg-red-50 text-red-800 border border-red-200"
                    }`}
                  >
                    <p className="font-medium mb-1">
                      {isCorrect ? "Correct!" : "Incorrect"}
                    </p>
                    <p>{scenario.explanation}</p>
                  </div>
                )}
              </section>
            );
          })}
        </div>

        {!submitted && (
          <div className="mt-6">
            <button
              onClick={handleSubmit}
              disabled={!allAnswered}
              className="w-full py-3 bg-brand-red text-white rounded-xl text-sm font-medium hover:bg-brand-red-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Submit Answers
            </button>
            {!allAnswered && (
              <p className="text-xs text-gray-400 text-center mt-2">
                Please answer all 3 scenarios to submit.
              </p>
            )}
          </div>
        )}

        {submitted && !allCorrect && (
          <div className="mt-6 flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-2xl p-4">
            <AlertTriangle
              className="w-5 h-5 text-amber-600 flex-shrink-0"
              aria-hidden="true"
            />
            <div>
              <p className="text-sm font-semibold text-amber-800">
                Some answers were incorrect
              </p>
              <p className="text-xs text-amber-600">
                Review the explanations above and try again in your next
                session.
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
