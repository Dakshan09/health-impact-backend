import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChevronLeft, ChevronRight, Check, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface FormData {
  // Personal Information
  fullName: string;
  email: string;
  age: string;
  gender: string;
  height: string;
  weight: string;
  ethnicity: string;
  location: string;

  // Health Status
  existingConditions: string[];
  currentMedications: string;
  familyHistory: string[];
  bloodPressure: string;
  fastingGlucose: string;
  cholesterol: string;

  // Diet & Nutrition
  processedFoodConsumption: string;
  sugarConsumption: string;
  waterIntake: string;
  dietType: string;
  mealFrequency: string;
  fruitVegServings: string;

  // Lifestyle
  exerciseFrequency: string;
  exerciseType: string;
  sleepHours: string;
  sleepQuality: string;
  smokingStatus: string;
  alcoholConsumption: string;
  stressLevel: string;
  screenTime: string;
}

const steps = [
  { id: 1, label: "Personal", icon: "👤" },
  { id: 2, label: "Health", icon: "🏥" },
  { id: 3, label: "Diet", icon: "🥗" },
  { id: 4, label: "Lifestyle", icon: "🏃" },
  { id: 5, label: "Review", icon: "✅" },
];

const PillOption = ({
  label,
  selected,
  onClick,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className={`px-4 py-2 rounded-full border text-sm font-medium transition-all duration-200 ${selected
      ? "bg-teal-500 border-teal-500 text-white"
      : "bg-white border-gray-300 text-gray-700 hover:border-teal-400 hover:text-teal-600"
      }`}
  >
    {label}
  </button>
);

const RadioOption = ({
  label,
  value,
  selected,
  onClick,
}: {
  label: string;
  value: string;
  selected: boolean;
  onClick: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className={`w-full text-left px-4 py-3 rounded-lg border text-sm font-medium transition-all duration-200 ${selected
      ? "bg-teal-50 border-teal-500 text-teal-700"
      : "bg-white border-gray-200 text-gray-700 hover:border-teal-300 hover:bg-teal-50/50"
      }`}
  >
    <span className={`inline-block w-4 h-4 rounded-full border-2 mr-3 align-middle ${selected ? "border-teal-500 bg-teal-500" : "border-gray-400"}`}></span>
    {label}
  </button>
);

const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <p className="text-xs font-semibold uppercase tracking-widest text-gray-500 mb-3">{children}</p>
);

const Assessment = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    fullName: "",
    email: "",
    age: "",
    gender: "",
    height: "",
    weight: "",
    ethnicity: "",
    location: "",
    existingConditions: ["None"],
    currentMedications: "",
    familyHistory: ["None"],
    bloodPressure: "",
    fastingGlucose: "",
    cholesterol: "",
    processedFoodConsumption: "",
    sugarConsumption: "",
    waterIntake: "",
    dietType: "",
    mealFrequency: "",
    fruitVegServings: "",
    exerciseFrequency: "",
    exerciseType: "",
    sleepHours: "",
    sleepQuality: "",
    smokingStatus: "",
    alcoholConsumption: "",
    stressLevel: "",
    screenTime: "",
  });

  const updateFormData = (field: keyof FormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const togglePill = (field: "existingConditions" | "familyHistory", value: string) => {
    setFormData((prev) => {
      const current = prev[field] as string[];
      if (value === "None") {
        return { ...prev, [field]: ["None"] };
      }
      const withoutNone = current.filter((c) => c !== "None");
      if (withoutNone.includes(value)) {
        const updated = withoutNone.filter((c) => c !== value);
        return { ...prev, [field]: updated.length === 0 ? ["None"] : updated };
      } else {
        return { ...prev, [field]: [...withoutNone, value] };
      }
    });
  };

  const handleNext = async () => {
    if (step < 5) {
      setStep(step + 1);
      window.scrollTo(0, 0);
    } else {
      setIsSubmitting(true);
      try {
        const apiBase = import.meta.env.VITE_API_BASE_URL || "";
        const response = await fetch(`${apiBase}/api/submit`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          mode: "cors",
          body: JSON.stringify({ patientData: formData }),
        });

        if (!response.ok) {
          throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        // Store everything in localStorage for Dashboard to read
        localStorage.setItem("patientData", JSON.stringify(formData));
        if (data?.analysis) {
          localStorage.setItem("lastAnalysis", data.analysis);
        }
        localStorage.setItem("submitResult", JSON.stringify({
          assessmentId: data.assessment_id || "",
          emailSent: data.email_sent || false,
          emailAddress: data.email_address || formData.email,
          overallRisk: data.overall_risk || "",
          riskCategories: data.risk_categories || {},
          lifestyleScores: data.lifestyle_scores || {},
        }));

        toast({
          title: "✅ Assessment Complete!",
          description: data.email_sent
            ? `Your reports have been generated and emailed to ${formData.email}.`
            : "Your health analysis is ready. Download your reports from the dashboard.",
        });
        navigate("/dashboard");
      } catch (error) {
        console.error("Error submitting:", error);
        // Save locally anyway and go to dashboard
        localStorage.setItem("patientData", JSON.stringify(formData));
        toast({
          title: "Assessment Saved",
          description: "Backend unavailable. Assessment saved locally — you can download reports from the dashboard.",
        });
        navigate("/dashboard");
      } finally {
        setIsSubmitting(false);
      }
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
      window.scrollTo(0, 0);
    }
  };

  const existingConditionOptions = ["None", "Hypertension", "Diabetes", "High Cholesterol", "Asthma", "Heart Disease", "Thyroid", "PCOS"];
  const familyHistoryOptions = ["None", "Diabetes", "Heart Disease", "Cancer", "Stroke", "Obesity", "Hypertension"];

  return (
    <div className="min-h-screen" style={{ background: "linear-gradient(135deg, #eef2ff 0%, #f0f9ff 50%, #ecfdf5 100%)" }}>
      {/* Header */}
      <div className="pt-10 pb-6 text-center">
        <div className="text-5xl mb-3">🧬</div>
        <h1 className="text-3xl font-extrabold" style={{ color: "#4338ca" }}>
          Health Impact Predictor
        </h1>
        <p className="text-gray-500 mt-2 text-base">AI-powered risk assessment &amp; personalized intervention plans</p>
      </div>

      {/* Step Indicator */}
      <div className="max-w-3xl mx-auto px-4 mb-8">
        <div className="flex items-center justify-center">
          {steps.map((s, i) => (
            <div key={s.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all ${s.id === step
                    ? "text-white shadow-lg"
                    : s.id < step
                      ? "text-white"
                      : "bg-white border-2 border-gray-200 text-gray-400"
                    }`}
                  style={
                    s.id === step
                      ? { background: "#14b8a6" }
                      : s.id < step
                        ? { background: "#14b8a6" }
                        : {}
                  }
                >
                  {s.id < step ? <Check className="w-5 h-5" /> : s.id}
                </div>
                <span
                  className={`text-xs mt-1 font-medium ${s.id === step ? "text-teal-600" : s.id < step ? "text-teal-500" : "text-gray-400"
                    }`}
                >
                  {s.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className="h-0.5 w-12 md:w-20 mx-1 mb-4"
                  style={{ background: step > s.id ? "#14b8a6" : "#e5e7eb" }}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Card */}
      <div className="max-w-3xl mx-auto px-4 pb-16">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          {/* Card top accent bar */}
          <div className="h-1" style={{ background: "linear-gradient(90deg, #7c3aed, #db2777)" }} />

          <div className="p-8">
            {/* Step 1: Personal Information */}
            {step === 1 && (
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">👤</span>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Personal Information</h2>
                    <p className="text-gray-500 text-sm">Basic demographic and physical details</p>
                  </div>
                </div>

                <div className="space-y-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">FULL NAME</label>
                      <Input
                        value={formData.fullName}
                        onChange={(e) => updateFormData("fullName", e.target.value)}
                        placeholder="e.g. Alex Chen"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">EMAIL</label>
                      <Input
                        type="email"
                        value={formData.email}
                        onChange={(e) => updateFormData("email", e.target.value)}
                        placeholder="alex@example.com"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">AGE</label>
                      <Input
                        type="number"
                        value={formData.age}
                        onChange={(e) => updateFormData("age", e.target.value)}
                        placeholder="30"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">GENDER</label>
                      <select
                        value={formData.gender}
                        onChange={(e) => updateFormData("gender", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="non-binary">Non-binary</option>
                        <option value="prefer-not-to-say">Prefer not to say</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">HEIGHT</label>
                      <Input
                        value={formData.height}
                        onChange={(e) => updateFormData("height", e.target.value)}
                        placeholder="175 cm / 5'9&quot;"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">WEIGHT</label>
                      <Input
                        value={formData.weight}
                        onChange={(e) => updateFormData("weight", e.target.value)}
                        placeholder="70 kg / 154 lbs"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">ETHNICITY</label>
                      <select
                        value={formData.ethnicity}
                        onChange={(e) => updateFormData("ethnicity", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select ethnicity</option>
                        <option value="asian">Asian</option>
                        <option value="black">Black / African American</option>
                        <option value="hispanic">Hispanic / Latino</option>
                        <option value="white">White / Caucasian</option>
                        <option value="middle-eastern">Middle Eastern</option>
                        <option value="south-asian">South Asian</option>
                        <option value="mixed">Mixed / Multiple</option>
                        <option value="other">Other</option>
                        <option value="prefer-not">Prefer not to say</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold uppercase tracking-widest text-gray-500 mb-2">LOCATION</label>
                      <select
                        value={formData.location}
                        onChange={(e) => updateFormData("location", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select country</option>
                        <option value="india">India</option>
                        <option value="usa">United States</option>
                        <option value="uk">United Kingdom</option>
                        <option value="canada">Canada</option>
                        <option value="australia">Australia</option>
                        <option value="uae">UAE</option>
                        <option value="singapore">Singapore</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Health Status */}
            {step === 2 && (
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">🏥</span>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Health Status</h2>
                    <p className="text-gray-500 text-sm">Current conditions and medical history</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <SectionLabel>EXISTING CONDITIONS</SectionLabel>
                    <div className="flex flex-wrap gap-2">
                      {existingConditionOptions.map((opt) => (
                        <PillOption
                          key={opt}
                          label={opt}
                          selected={formData.existingConditions.includes(opt)}
                          onClick={() => togglePill("existingConditions", opt)}
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <SectionLabel>CURRENT MEDICATIONS</SectionLabel>
                    <Input
                      value={formData.currentMedications}
                      onChange={(e) => updateFormData("currentMedications", e.target.value)}
                      placeholder="e.g. Metformin, Atorvastatin (or 'None')"
                      className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                    />
                  </div>

                  <div>
                    <SectionLabel>FAMILY HISTORY</SectionLabel>
                    <div className="flex flex-wrap gap-2">
                      {familyHistoryOptions.map((opt) => (
                        <PillOption
                          key={opt}
                          label={opt}
                          selected={formData.familyHistory.includes(opt)}
                          onClick={() => togglePill("familyHistory", opt)}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <SectionLabel>BLOOD PRESSURE</SectionLabel>
                      <Input
                        value={formData.bloodPressure}
                        onChange={(e) => updateFormData("bloodPressure", e.target.value)}
                        placeholder="e.g. 120/80 mmHg"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <SectionLabel>FASTING GLUCOSE</SectionLabel>
                      <Input
                        value={formData.fastingGlucose}
                        onChange={(e) => updateFormData("fastingGlucose", e.target.value)}
                        placeholder="e.g. 90 mg/dL"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                  </div>

                  <div>
                    <SectionLabel>CHOLESTEROL (TOTAL)</SectionLabel>
                    <Input
                      value={formData.cholesterol}
                      onChange={(e) => updateFormData("cholesterol", e.target.value)}
                      placeholder="e.g. 200 mg/dL"
                      className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Diet & Nutrition */}
            {step === 3 && (
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">🥗</span>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Diet &amp; Nutrition</h2>
                    <p className="text-gray-500 text-sm">Your eating habits and dietary patterns</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <SectionLabel>PROCESSED FOOD CONSUMPTION</SectionLabel>
                    <div className="space-y-2">
                      {["Rarely (less than once a week)", "Occasionally (1-2 times a week)", "Frequently (3-5 times a week)", "Daily"].map((opt) => (
                        <RadioOption
                          key={opt}
                          label={opt}
                          value={opt}
                          selected={formData.processedFoodConsumption === opt}
                          onClick={() => updateFormData("processedFoodConsumption", opt)}
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <SectionLabel>SUGAR CONSUMPTION</SectionLabel>
                    <div className="space-y-2">
                      {["Low (minimal sweets/sugary drinks)", "Moderate (occasional sweets)", "High (daily sweets/sugary drinks)", "Very High (multiple times daily)"].map((opt) => (
                        <RadioOption
                          key={opt}
                          label={opt}
                          value={opt}
                          selected={formData.sugarConsumption === opt}
                          onClick={() => updateFormData("sugarConsumption", opt)}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <SectionLabel>WATER INTAKE (CUPS/DAY)</SectionLabel>
                      <Input
                        type="number"
                        value={formData.waterIntake}
                        onChange={(e) => updateFormData("waterIntake", e.target.value)}
                        placeholder="e.g. 8"
                        min="0"
                        max="30"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <SectionLabel>DIET TYPE</SectionLabel>
                      <select
                        value={formData.dietType}
                        onChange={(e) => updateFormData("dietType", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select diet type</option>
                        <option value="omnivore">Omnivore</option>
                        <option value="vegetarian">Vegetarian</option>
                        <option value="vegan">Vegan</option>
                        <option value="pescatarian">Pescatarian</option>
                        <option value="keto">Keto</option>
                        <option value="mediterranean">Mediterranean</option>
                        <option value="paleo">Paleo</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <SectionLabel>MEALS PER DAY</SectionLabel>
                      <Input
                        type="number"
                        value={formData.mealFrequency}
                        onChange={(e) => updateFormData("mealFrequency", e.target.value)}
                        placeholder="e.g. 3"
                        min="1"
                        max="10"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <SectionLabel>FRUIT &amp; VEG SERVINGS/DAY</SectionLabel>
                      <Input
                        type="number"
                        value={formData.fruitVegServings}
                        onChange={(e) => updateFormData("fruitVegServings", e.target.value)}
                        placeholder="e.g. 5"
                        min="0"
                        max="20"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Lifestyle */}
            {step === 4 && (
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">🏃</span>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Lifestyle</h2>
                    <p className="text-gray-500 text-sm">Physical activity, sleep &amp; daily habits</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <SectionLabel>EXERCISE FREQUENCY</SectionLabel>
                    <div className="space-y-2">
                      {[
                        "Sedentary (little to no exercise)",
                        "Light (1-2 days/week)",
                        "Moderate (3-4 days/week)",
                        "Active (5-6 days/week)",
                        "Very Active (daily intense exercise)",
                      ].map((opt) => (
                        <RadioOption
                          key={opt}
                          label={opt}
                          value={opt}
                          selected={formData.exerciseFrequency === opt}
                          onClick={() => updateFormData("exerciseFrequency", opt)}
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <SectionLabel>EXERCISE TYPE</SectionLabel>
                    <div className="space-y-2">
                      {["Cardio (Running, Cycling, Swimming)", "Strength Training (Weights, Resistance)", "Flexibility (Yoga, Stretching)", "Mixed / Cross Training", "Sports / Recreational"].map((opt) => (
                        <RadioOption
                          key={opt}
                          label={opt}
                          value={opt}
                          selected={formData.exerciseType === opt}
                          onClick={() => updateFormData("exerciseType", opt)}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <SectionLabel>SLEEP HOURS / NIGHT</SectionLabel>
                      <Input
                        type="number"
                        value={formData.sleepHours}
                        onChange={(e) => updateFormData("sleepHours", e.target.value)}
                        placeholder="e.g. 7"
                        min="1"
                        max="24"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                    <div>
                      <SectionLabel>SLEEP QUALITY</SectionLabel>
                      <select
                        value={formData.sleepQuality}
                        onChange={(e) => updateFormData("sleepQuality", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select sleep quality</option>
                        <option value="excellent">Excellent</option>
                        <option value="good">Good</option>
                        <option value="fair">Fair</option>
                        <option value="poor">Poor</option>
                        <option value="very-poor">Very Poor (insomnia)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <SectionLabel>SMOKING STATUS</SectionLabel>
                      <select
                        value={formData.smokingStatus}
                        onChange={(e) => updateFormData("smokingStatus", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select status</option>
                        <option value="never">Never smoked</option>
                        <option value="former">Former smoker</option>
                        <option value="occasional">Current (occasional)</option>
                        <option value="daily">Current (daily)</option>
                        <option value="heavy">Heavy smoker (20+ /day)</option>
                      </select>
                    </div>
                    <div>
                      <SectionLabel>ALCOHOL CONSUMPTION</SectionLabel>
                      <select
                        value={formData.alcoholConsumption}
                        onChange={(e) => updateFormData("alcoholConsumption", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select frequency</option>
                        <option value="never">Never</option>
                        <option value="rarely">Rarely (special occasions)</option>
                        <option value="monthly">Monthly</option>
                        <option value="weekly">Weekly</option>
                        <option value="daily">Daily</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <SectionLabel>STRESS LEVEL</SectionLabel>
                      <select
                        value={formData.stressLevel}
                        onChange={(e) => updateFormData("stressLevel", e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-gray-200 bg-gray-50 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400 focus:bg-white"
                      >
                        <option value="">Select level</option>
                        <option value="low">Low</option>
                        <option value="moderate">Moderate</option>
                        <option value="high">High</option>
                        <option value="very-high">Very High (chronic)</option>
                      </select>
                    </div>
                    <div>
                      <SectionLabel>DAILY SCREEN TIME (HRS)</SectionLabel>
                      <Input
                        type="number"
                        value={formData.screenTime}
                        onChange={(e) => updateFormData("screenTime", e.target.value)}
                        placeholder="e.g. 6"
                        min="0"
                        max="24"
                        className="rounded-xl border-gray-200 bg-gray-50 focus:bg-white"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 5: Review */}
            {step === 5 && (
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-3xl">✅</span>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Review Your Information</h2>
                    <p className="text-gray-500 text-sm">Please review your details before submitting</p>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* Personal */}
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <span>👤</span> Personal Information
                    </h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div><span className="text-gray-500">Name:</span> <span className="text-gray-800">{formData.fullName || "—"}</span></div>
                      <div><span className="text-gray-500">Email:</span> <span className="text-gray-800">{formData.email || "—"}</span></div>
                      <div><span className="text-gray-500">Age:</span> <span className="text-gray-800">{formData.age || "—"}</span></div>
                      <div><span className="text-gray-500">Gender:</span> <span className="text-gray-800">{formData.gender || "—"}</span></div>
                      <div><span className="text-gray-500">Height:</span> <span className="text-gray-800">{formData.height || "—"}</span></div>
                      <div><span className="text-gray-500">Weight:</span> <span className="text-gray-800">{formData.weight || "—"}</span></div>
                      <div><span className="text-gray-500">Ethnicity:</span> <span className="text-gray-800">{formData.ethnicity || "—"}</span></div>
                      <div><span className="text-gray-500">Location:</span> <span className="text-gray-800">{formData.location || "—"}</span></div>
                    </div>
                  </div>

                  {/* Health */}
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <span>🏥</span> Health Status
                    </h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="col-span-2"><span className="text-gray-500">Conditions:</span> <span className="text-gray-800">{formData.existingConditions.join(", ")}</span></div>
                      <div className="col-span-2"><span className="text-gray-500">Medications:</span> <span className="text-gray-800">{formData.currentMedications || "None"}</span></div>
                      <div className="col-span-2"><span className="text-gray-500">Family History:</span> <span className="text-gray-800">{formData.familyHistory.join(", ")}</span></div>
                      <div><span className="text-gray-500">Blood Pressure:</span> <span className="text-gray-800">{formData.bloodPressure || "—"}</span></div>
                      <div><span className="text-gray-500">Fasting Glucose:</span> <span className="text-gray-800">{formData.fastingGlucose || "—"}</span></div>
                      <div><span className="text-gray-500">Cholesterol:</span> <span className="text-gray-800">{formData.cholesterol || "—"}</span></div>
                    </div>
                  </div>

                  {/* Diet */}
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <span>🥗</span> Diet &amp; Nutrition
                    </h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div><span className="text-gray-500">Diet Type:</span> <span className="text-gray-800">{formData.dietType || "—"}</span></div>
                      <div><span className="text-gray-500">Water Intake:</span> <span className="text-gray-800">{formData.waterIntake ? `${formData.waterIntake} cups/day` : "—"}</span></div>
                      <div><span className="text-gray-500">Meals/Day:</span> <span className="text-gray-800">{formData.mealFrequency || "—"}</span></div>
                      <div><span className="text-gray-500">Fruit &amp; Veg:</span> <span className="text-gray-800">{formData.fruitVegServings ? `${formData.fruitVegServings} servings` : "—"}</span></div>
                      <div className="col-span-2"><span className="text-gray-500">Processed Food:</span> <span className="text-gray-800">{formData.processedFoodConsumption || "—"}</span></div>
                    </div>
                  </div>

                  {/* Lifestyle */}
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                      <span>🏃</span> Lifestyle
                    </h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div><span className="text-gray-500">Exercise:</span> <span className="text-gray-800">{formData.exerciseFrequency || "—"}</span></div>
                      <div><span className="text-gray-500">Sleep:</span> <span className="text-gray-800">{formData.sleepHours ? `${formData.sleepHours} hrs` : "—"}</span></div>
                      <div><span className="text-gray-500">Smoking:</span> <span className="text-gray-800">{formData.smokingStatus || "—"}</span></div>
                      <div><span className="text-gray-500">Alcohol:</span> <span className="text-gray-800">{formData.alcoholConsumption || "—"}</span></div>
                      <div><span className="text-gray-500">Stress:</span> <span className="text-gray-800">{formData.stressLevel || "—"}</span></div>
                      <div><span className="text-gray-500">Screen Time:</span> <span className="text-gray-800">{formData.screenTime ? `${formData.screenTime} hrs/day` : "—"}</span></div>
                    </div>
                  </div>

                  <div className="bg-teal-50 border border-teal-200 rounded-xl p-4 text-sm text-teal-800">
                    <strong>⚕️ Medical Disclaimer:</strong> This assessment is for informational purposes only and does not constitute medical advice. Always consult with qualified healthcare professionals for proper diagnosis and treatment.
                  </div>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-100">
              <Button
                variant="outline"
                onClick={handleBack}
                disabled={step === 1}
                className="flex items-center gap-2 rounded-xl px-6"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </Button>

              <Button
                onClick={handleNext}
                disabled={isSubmitting}
                className="flex items-center gap-2 rounded-xl px-8 text-white font-semibold"
                style={{ background: "linear-gradient(135deg, #7c3aed, #db2777)" }}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating reports & emailing...
                  </>
                ) : step === 5 ? (
                  <>
                    <span>🚀</span>
                    Generate Health Analysis
                  </>
                ) : (
                  <>
                    Continue
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Footer Disclaimer */}
        <p className="text-center text-xs text-gray-400 mt-6">
          <strong>Medical Disclaimer:</strong> This tool is for informational purposes only and is not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  );
};

export default Assessment;
