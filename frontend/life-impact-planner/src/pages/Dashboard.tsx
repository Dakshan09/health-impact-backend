import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import {
  Activity,
  AlertTriangle,
  Heart,
  TrendingUp,
  User,
  FileText,
  ArrowLeft,
  CheckCircle2,
  Download,
  BarChart3,
  Calendar,
  Loader2,
} from "lucide-react";

let envUrl = import.meta.env.VITE_API_BASE_URL || "https://health-impact-backend.onrender.com";
if (envUrl === "/" || envUrl === "") envUrl = "https://health-impact-backend.onrender.com";
const API_BASE = envUrl.replace(/\/$/, "");

const Dashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [patientData, setPatientData] = useState<any>(null);
  const [analysis, setAnalysis] = useState<string>("");
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [downloading, setDownloading] = useState<{
    clinical: boolean;
    visualization: boolean;
    schedule: boolean;
  }>({ clinical: false, visualization: false, schedule: false });

  useEffect(() => {
    const data = localStorage.getItem("patientData");
    const savedAnalysis = localStorage.getItem("lastAnalysis");
    const savedResult = localStorage.getItem("submitResult");
    if (!data) {
      navigate("/");
      return;
    }
    setPatientData(JSON.parse(data));
    if (savedAnalysis) setAnalysis(savedAnalysis);
    if (savedResult) setSubmitResult(JSON.parse(savedResult));
  }, [navigate]);

  if (!patientData) {
    return null;
  }

  // ─── Risk Calculation ────────────────────────────────────────────────────
  const calculateRiskScore = () => {
    let score = 0;
    let maxScore = 0;

    const age = parseInt(patientData.age);
    if (age > 65) score += 3;
    else if (age > 50) score += 2;
    else if (age > 35) score += 1;
    maxScore += 3;

    const conditions = patientData.existingConditions || patientData.conditions || [];
    score += Math.min(conditions.length * 2, 6);
    maxScore += 6;

    if (patientData.smokingStatus?.includes("daily")) score += 4;
    else if (patientData.smokingStatus?.includes("occasional")) score += 2;
    maxScore += 4;

    if (patientData.exerciseFrequency?.includes("Sedentary")) score += 3;
    else if (patientData.exerciseFrequency?.includes("Light")) score += 1;
    maxScore += 3;

    const sleep = parseInt(patientData.sleepHours);
    if (sleep < 6 || sleep > 9) score += 2;
    maxScore += 2;

    if (patientData.stressLevel === "High") score += 3;
    else if (patientData.stressLevel === "Medium") score += 1;
    maxScore += 3;

    if (patientData.alcoholConsumption?.includes("Frequent")) score += 2;
    maxScore += 2;

    const percentage = Math.round((score / maxScore) * 100);
    return { score, maxScore, percentage };
  };

  const riskScore = calculateRiskScore();

  const getRiskLevel = (percentage: number) => {
    if (percentage < 30) return { level: "Low Risk", color: "text-green-600 bg-green-50", icon: CheckCircle2 };
    if (percentage < 60) return { level: "Moderate Risk", color: "text-yellow-600 bg-yellow-50", icon: AlertTriangle };
    return { level: "High Risk", color: "text-red-600 bg-red-50", icon: AlertTriangle };
  };

  const risk = getRiskLevel(riskScore.percentage);
  const RiskIcon = risk.icon;

  // ─── Report Download ──────────────────────────────────────────────────────
  const downloadReport = async (type: "clinical" | "visualization" | "schedule") => {
    setDownloading((prev) => ({ ...prev, [type]: true }));

    try {
      const response = await fetch(`${API_BASE}/api/report/${type}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patientData,
          analysis: analysis || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      // Detect filename from content-disposition header
      const contentDisposition = response.headers.get("content-disposition") || "";
      const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      const fileName = fileNameMatch
        ? fileNameMatch[1].replace(/['"]/g, "")
        : `${type}_report.pdf`;

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      const labels = {
        clinical: "Clinical PDF",
        visualization: "Visualization Report",
        schedule: "Schedule (Excel)",
      };
      toast({
        title: "Download started",
        description: `${labels[type]} is downloading.`,
      });
    } catch (err: any) {
      toast({
        title: "Download failed",
        description: err.message || "Could not generate report. Is the server running?",
        variant: "destructive",
      });
    } finally {
      setDownloading((prev) => ({ ...prev, [type]: false }));
    }
  };

  // ─── JSX ──────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="mb-4 flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Button>
          <h1 className="text-4xl font-bold text-foreground mb-2">Health Assessment Dashboard</h1>
          <p className="text-muted-foreground">
            Based on your assessment completed on {new Date().toLocaleDateString()}
          </p>
        </div>

        {/* Email Confirmation Banner */}
        {submitResult?.emailSent && (
          <div className="mb-6 p-4 rounded-xl border-2 border-green-300 bg-green-50 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-green-800">Reports emailed successfully! 📧</p>
              <p className="text-sm text-green-700 mt-0.5">
                Your Clinical Report, Visualization Report, and 90-Day Schedule have been sent to{" "}
                <strong>{submitResult.emailAddress}</strong>. Check your inbox (and spam folder if needed).
              </p>
              {submitResult.assessmentId && (
                <p className="text-xs text-green-600 mt-1">Assessment ID: {submitResult.assessmentId}</p>
              )}
            </div>
          </div>
        )}
        {submitResult && !submitResult.emailSent && submitResult.assessmentId && (
          <div className="mb-6 p-4 rounded-xl border-2 border-blue-200 bg-blue-50 flex items-start gap-3">
            <FileText className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-blue-800">Assessment saved to database ✅</p>
              <p className="text-sm text-blue-700 mt-0.5">
                Reports generated — email not configured yet. Download them below.
              </p>
            </div>
          </div>
        )}

        {/* Top cards: profile + risk */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Patient Info */}
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 rounded-full bg-accent">
                <User className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Patient Profile</h3>
                <p className="text-sm text-muted-foreground">Personal Information</p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Name:</span>
                <span className="font-medium">{patientData.fullName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Age:</span>
                <span className="font-medium">{patientData.age} years</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Gender:</span>
                <span className="font-medium capitalize">{patientData.gender}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Email:</span>
                <span className="font-medium text-xs">{patientData.email}</span>
              </div>
            </div>
          </Card>

          {/* Risk Score */}
          <Card className="p-6 lg:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-full bg-accent">
                <Activity className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">Overall Health Risk Assessment</h3>
                <p className="text-sm text-muted-foreground">Long-term impact analysis</p>
              </div>
            </div>

            <div className="flex items-center gap-8">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="none" className="text-muted" />
                  <circle
                    cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="none"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (1 - riskScore.percentage / 100)}`}
                    className="text-primary transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-3xl font-bold text-foreground">{riskScore.percentage}%</div>
                </div>
              </div>
              <div className="flex-1">
                <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${risk.color} mb-4`}>
                  <RiskIcon className="w-5 h-5" />
                  <span className="font-semibold">{risk.level}</span>
                </div>
                <p className="text-sm text-muted-foreground mb-2">
                  Based on your medical history, lifestyle factors, and current health status.
                </p>
                <p className="text-sm text-foreground font-medium">
                  Risk Score: {riskScore.score} / {riskScore.maxScore} factors identified
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Risk Factor Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {((patientData.existingConditions || patientData.conditions || []).filter((c: string) => c !== 'None').length > 0) && (
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-red-50">
                  <Heart className="w-5 h-5 text-red-600" />
                </div>
                <h3 className="font-semibold text-foreground">Medical Conditions</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {(patientData.existingConditions || patientData.conditions || []).map((condition: string) => (
                  <Badge key={condition} variant="outline" className="text-xs">{condition}</Badge>
                ))}
              </div>
            </Card>
          )}

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-accent">
                <TrendingUp className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground">Lifestyle Impact</h3>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Exercise:</span>
                <span className="font-medium">{patientData.exerciseFrequency?.split(" ")[0] || "N/A"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Sleep:</span>
                <span className="font-medium">{patientData.sleepHours || "N/A"}h average</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Stress:</span>
                <span className="font-medium">{patientData.stressLevel || "N/A"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Smoking:</span>
                <span className="font-medium">{patientData.smokingStatus?.split(" ")[0] || "N/A"}</span>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-accent">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground">Diet & Nutrition</h3>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Diet Type:</span>
                <span className="font-medium capitalize">{patientData.dietType || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Water Intake:</span>
                <span className="font-medium">{patientData.waterIntake ? `${patientData.waterIntake} cups/day` : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Meals/Day:</span>
                <span className="font-medium">{patientData.mealFrequency || 'N/A'}</span>
              </div>
            </div>
          </Card>
        </div>

        {/* ────────── REPORT DOWNLOADS ────────── */}
        <Card className="p-6 mb-8 border-2 border-primary/20 bg-gradient-to-br from-accent/30 to-background">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <Download className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-foreground">Download Reports</h3>
              <p className="text-sm text-muted-foreground">
                Generate and download your personalized health reports
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            {/* Clinical Report */}
            <div className="flex flex-col gap-3 p-4 rounded-lg border border-border bg-background hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-50">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-foreground text-sm">Clinical Report</h4>
                  <p className="text-xs text-muted-foreground">PDF · Medical analysis</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Full text-based medical report with risk tables, AI analysis and recommendations.
                Suitable for sharing with your doctor.
              </p>
              <Button
                onClick={() => downloadReport("clinical")}
                disabled={downloading.clinical}
                size="sm"
                className="mt-auto w-full flex items-center gap-2"
              >
                {downloading.clinical ? (
                  <><Loader2 className="w-3 h-3 animate-spin" /> Generating...</>
                ) : (
                  <><Download className="w-3 h-3" /> Download PDF</>
                )}
              </Button>
            </div>

            {/* Visualization Report */}
            <div className="flex flex-col gap-3 p-4 rounded-lg border border-border bg-background hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-50">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-foreground text-sm">Visualization Report</h4>
                  <p className="text-xs text-muted-foreground">PDF/HTML · Risk charts</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Visual report with color-coded risk bar charts for all categories and lifestyle quality scores.
              </p>
              <Button
                onClick={() => downloadReport("visualization")}
                disabled={downloading.visualization}
                size="sm"
                variant="secondary"
                className="mt-auto w-full flex items-center gap-2"
              >
                {downloading.visualization ? (
                  <><Loader2 className="w-3 h-3 animate-spin" /> Generating...</>
                ) : (
                  <><Download className="w-3 h-3" /> Download Report</>
                )}
              </Button>
            </div>

            {/* Schedule Report */}
            <div className="flex flex-col gap-3 p-4 rounded-lg border border-border bg-background hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-50">
                  <Calendar className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-foreground text-sm">90-Day Schedule</h4>
                  <p className="text-xs text-muted-foreground">Excel · Intervention plan</p>
                </div>
              </div>
              <p className="text-xs text-muted-foreground">
                Personalized 90-day intervention schedule with daily habits, milestones and weekly goals in Excel.
              </p>
              <Button
                onClick={() => downloadReport("schedule")}
                disabled={downloading.schedule}
                size="sm"
                variant="outline"
                className="mt-auto w-full flex items-center gap-2 border-green-600 text-green-700 hover:bg-green-50"
              >
                {downloading.schedule ? (
                  <><Loader2 className="w-3 h-3 animate-spin" /> Generating...</>
                ) : (
                  <><Download className="w-3 h-3" /> Download Excel</>
                )}
              </Button>
            </div>
          </div>
        </Card>

        {/* Recommendations */}
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-foreground mb-4">Recommendations for Long-term Health</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-accent">
              <h4 className="font-medium text-foreground mb-2">&#10003; Immediate Actions</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Schedule a comprehensive check-up with your primary care physician</li>
                <li>• Discuss your risk factors and current symptoms with a healthcare provider</li>
                <li>• Keep a daily health journal to track symptoms and lifestyle patterns</li>
              </ul>
            </div>
            <div className="p-4 rounded-lg bg-accent">
              <h4 className="font-medium text-foreground mb-2">&#10003; Lifestyle Improvements</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Aim for 150 minutes of moderate exercise per week</li>
                <li>• Maintain consistent sleep schedule (7-9 hours nightly)</li>
                <li>• Implement stress management techniques (meditation, yoga)</li>
                <li>• Follow a balanced diet rich in fruits and vegetables</li>
              </ul>
            </div>
          </div>
        </Card>

        {/* Disclaimer */}
        <div className="mt-8 p-4 rounded-lg bg-muted">
          <p className="text-sm text-muted-foreground text-center">
            <strong>Medical Disclaimer:</strong> This assessment is for informational purposes only and does not
            constitute medical advice. Always consult with qualified healthcare professionals for proper diagnosis
            and treatment.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
