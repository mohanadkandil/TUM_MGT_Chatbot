import React from "react";
import { faqData, FaqSection } from "@/lib/data";
import { useSelectedQuestionStore } from "@/lib/stores/useSelectedQuestionStore";

export function QuestionsRecommendation() {
  const setSelectedQuestion = useSelectedQuestionStore(
    (state) => state.setSelectedQuestion
  );
  const handleQuestionClick = (answer: string) => {
    setSelectedQuestion(answer);
  };

  return (
    <div className="mx-auto flex flex-wrap items-center gap-4 w-fit pl-12">
      {Object.values(faqData).map((section: FaqSection) => (
        <div key={section.title} className="bg-[#F1F5F9] p-6 rounded-2xl">
          <h3 className="text-2xl font-semibold">{section.title}</h3>
          <div className="flex flex-col justify-between gap-6 pt-6 sm:w-[280px] w-full">
            {Object.entries(section.questions).map(([question, answer]) => (
              <div
                key={question}
                className="bg-white rounded-full px-4 py-2 w-fit cursor-pointer"
                onClick={() => handleQuestionClick(answer)}
              >
                <p className="text-sm font-medium text-[#1A3048]">{question}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
