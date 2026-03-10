import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  webhookResponse: any;
  onClose: () => void;
  onGoToDashboard: () => void;
}

export const ChatInterface = ({ webhookResponse, onClose, onGoToDashboard }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    // Add user message
    setMessages([
      {
        role: "user",
        content: "I've completed my health assessment. Can you analyze my results?",
        timestamp: new Date(),
      },
    ]);

    // Simulate AI typing and then show response
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      
      // Format webhook response as assistant message
      let assistantMessage = "";
      
      if (webhookResponse) {
        if (typeof webhookResponse === "string") {
          assistantMessage = webhookResponse;
        } else if (webhookResponse.message) {
          assistantMessage = webhookResponse.message;
        } else if (webhookResponse.analysis) {
          assistantMessage = webhookResponse.analysis;
        } else if (webhookResponse.result) {
          assistantMessage = webhookResponse.result;
        } else {
          // Format the entire response nicely
          assistantMessage = "Assessment received successfully!\n\n";
          Object.entries(webhookResponse).forEach(([key, value]) => {
            assistantMessage += `**${key}**: ${JSON.stringify(value, null, 2)}\n`;
          });
        }
      } else {
        assistantMessage = "Your health assessment has been received and processed successfully. You can now view your detailed analysis in the dashboard.";
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: assistantMessage,
          timestamp: new Date(),
        },
      ]);
    }, 1500);
  }, [webhookResponse]);

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-3xl h-[600px] flex flex-col">
        <div className="p-4 border-b bg-gradient-to-r from-primary/10 to-secondary/10">
          <h2 className="text-xl font-semibold">Health Assessment Analysis</h2>
          <p className="text-sm text-muted-foreground">AI-powered health insights</p>
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <span className="text-xs opacity-70 mt-2 block">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>

                {message.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-secondary" />
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="bg-muted rounded-lg p-4">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground/50 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="p-4 border-t flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button onClick={onGoToDashboard}>
            View Full Dashboard
          </Button>
        </div>
      </Card>
    </div>
  );
};
