import * as React from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Define a TypeScript interface for the Major
interface Major {
  id: string;
  name: string;
  category: string;
}

// An array of majors typed with the Major interface
const majors: Major[] = [
  {
    id: "BMT-munich",
    name: "Management & Technology - Munich",
    category: "Bachelor Programs",
  },
  {
    id: "BMT-heilbronn",
    name: "Management & Technology - Heilbronn",
    category: "Bachelor Programs",
  },
  {
    id: "BSM",
    name: "Bachelor Sustainable Management",
    category: "Master Programs",
  },
  {
    id: "MMT",
    name: "Master Management & Technology",
    category: "Master Programs",
  },
  {
    id: "MMT-heilbronn",
    name: "Master Management & Digital Technology - Heilbronn",
    category: "Master Programs",
  },
  {
    id: "MSMT",
    name: "Master Sustainable Management & Technology",
    category: "Master Programs",
  },
  {
    id: "MFIT",
    name: "Master Finance & Information Technology",
    category: "Master Programs",
  },
  {
    id: "MM-munich",
    name: "Master Management - Munich",
    category: "Master Programs",
  },
  {
    id: "MM-heilbronn",
    name: "Master Mangement - Heilbronn",
    category: "Master Programs",
  },
  {
    id: "MCS",
    name: "Master Computer Science",
    category: "Master Programs",
  },
];

function MajorsFilter() {
  // You can filter and map over the majors array to dynamically generate your select options
  const groupedMajors = majors.reduce<Record<string, Major[]>>((acc, major) => {
    acc[major.category] = acc[major.category] || [];
    acc[major.category].push(major);
    return acc;
  }, {});

  return (
    <div className="flex w-full mx-auto max-w-3xl justify-end py-2 px-10 md:px-0">
      <Select>
        <SelectTrigger className="w-[204px]">
          <SelectValue placeholder="Select your program" />
        </SelectTrigger>
        <SelectContent>
          {Object.entries(groupedMajors).map(([category, majorsInCategory]) => (
            <SelectGroup key={category}>
              <SelectLabel>{category}</SelectLabel>
              {majorsInCategory.map((major) => (
                <SelectItem key={major.id} value={major.id}>
                  {major.name}
                </SelectItem>
              ))}
            </SelectGroup>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

export default MajorsFilter;
