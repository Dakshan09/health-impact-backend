import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { 
  Heart, 
  Activity, 
  ShieldCheck, 
  TrendingUp, 
  FileText,
  Clock,
  CheckCircle2,
  ArrowRight
} from "lucide-react";
import heroImage from "@/assets/hero-medical.jpg";

const Index = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: FileText,
      title: "Comprehensive Assessment",
      description: "Detailed health questionnaire covering medical history, lifestyle, and current symptoms."
    },
    {
      icon: Activity,
      title: "Risk Analysis",
      description: "Advanced algorithms evaluate your long-term health risks based on multiple factors."
    },
    {
      icon: TrendingUp,
      title: "Personalized Insights",
      description: "Receive tailored recommendations to improve your long-term health outcomes."
    },
    {
      icon: ShieldCheck,
      title: "Secure & Private",
      description: "Your health data is stored securely and remains completely confidential."
    }
  ];

  const benefits = [
    "Identify potential health risks early",
    "Track your health trends over time",
    "Make informed lifestyle decisions",
    "Get personalized health recommendations"
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-secondary/10" />
        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent border border-primary/20">
                <Heart className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-accent-foreground">
                  Advanced Health Assessment
                </span>
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold text-foreground leading-tight">
                Understand Your
                <span className="block bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  Long-term Health Impact
                </span>
              </h1>

              <p className="text-lg text-muted-foreground leading-relaxed">
                Take control of your health journey with our comprehensive assessment tool. 
                Get personalized insights and actionable recommendations based on your unique health profile.
              </p>

              <div className="flex flex-wrap gap-4">
                <Button
                  variant="hero"
                  size="lg"
                  onClick={() => navigate("/assessment")}
                  className="group"
                >
                  Start Your Assessment
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  onClick={() => {
                    document.getElementById("features")?.scrollIntoView({ behavior: "smooth" });
                  }}
                >
                  Learn More
                </Button>
              </div>

              <div className="flex items-center gap-6 pt-4">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-primary" />
                  <span className="text-sm text-muted-foreground">10 min assessment</span>
                </div>
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-primary" />
                  <span className="text-sm text-muted-foreground">100% confidential</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-secondary/20 rounded-3xl blur-3xl" />
              <img
                src={heroImage}
                alt="Medical health assessment"
                className="relative rounded-3xl shadow-2xl w-full h-auto object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              Why Choose Our Assessment?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Our comprehensive health assessment combines medical expertise with advanced analytics 
              to provide you with actionable insights.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={index}
                  className="p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-card"
                >
                  <div className="p-3 rounded-lg bg-accent w-fit mb-4">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-foreground mb-6">
                Take Charge of Your Health Future
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Our assessment helps you understand the potential long-term impacts of your 
                current health status and lifestyle choices, empowering you to make positive changes today.
              </p>

              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="p-1 rounded-full bg-primary/10">
                      <CheckCircle2 className="w-5 h-5 text-primary" />
                    </div>
                    <span className="text-foreground">{benefit}</span>
                  </div>
                ))}
              </div>

              <Button
                variant="hero"
                size="lg"
                onClick={() => navigate("/assessment")}
                className="mt-8"
              >
                Get Started Now
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
                <div className="text-4xl font-bold text-primary mb-2">10+</div>
                <div className="text-sm text-muted-foreground">Health Categories</div>
              </Card>
              <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 mt-8">
                <div className="text-4xl font-bold text-secondary mb-2">50+</div>
                <div className="text-sm text-muted-foreground">Data Points Analyzed</div>
              </Card>
              <Card className="p-6 text-center bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
                <div className="text-4xl font-bold text-primary mb-2">100%</div>
                <div className="text-sm text-muted-foreground">Secure & Private</div>
              </Card>
              <Card className="p-6 text-center bg-gradient-to-br from-secondary/5 to-secondary/10 border-secondary/20 mt-8">
                <div className="text-4xl font-bold text-secondary mb-2">24/7</div>
                <div className="text-sm text-muted-foreground">Access Anytime</div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-primary to-secondary">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Assess Your Health?
          </h2>
          <p className="text-lg text-white/90 mb-8 max-w-2xl mx-auto">
            Start your comprehensive health assessment today and take the first step 
            toward understanding your long-term health impact.
          </p>
          <Button
            size="lg"
            variant="secondary"
            onClick={() => navigate("/assessment")}
            className="shadow-xl hover:shadow-2xl bg-white text-primary hover:bg-white/90"
          >
            Begin Assessment
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto text-center">
          <p className="text-sm text-muted-foreground">
            <strong>Medical Disclaimer:</strong> This assessment tool is for informational purposes only 
            and does not constitute medical advice. Always consult with qualified healthcare professionals 
            for proper diagnosis and treatment.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
