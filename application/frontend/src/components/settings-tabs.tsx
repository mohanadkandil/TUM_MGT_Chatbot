import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { IconDatabase, IconSettings } from "./icons";
import { Switch } from "./ui/switch";
import { ThemeToggle } from "./sidebar/theme-toggle";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function SettingsTabs() {
  return (
    <div className="flex h-[550px]">
      <Tabs defaultValue="account" className="w-full flex">
        <TabsList className="flex flex-col items-start pr-10">
          <TabsTrigger value="account">
            <IconSettings className="mr-2" />
            <span className="text-meduim text-sm">General</span>
          </TabsTrigger>
          <TabsTrigger value="password">
            <IconDatabase className="mr-2" />
            <span className="text-meduim text-sm">Data Controls</span>
          </TabsTrigger>
        </TabsList>
        <div className="flex-grow">
          <TabsContent value="account" className="space-y-4">
            <Card className="flex items-center">
              <CardHeader className="flex-1">
                <CardTitle className="font-medium text-base">Theme</CardTitle>
                <CardDescription className="text-xs">
                  Horem ipsum dolor sit amet, consectetur adipiscing elit.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <ThemeToggle />
                </div>
              </CardContent>
            </Card>
            <Card className="flex items-center">
              <CardHeader>
                <CardTitle className="font-medium text-base">
                  Language
                </CardTitle>
                <CardDescription className="text-xs">
                  Horem ipsum dolor sit amet, consectetur adipiscing elit.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Select>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select a language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem value="english">English</SelectItem>
                      <SelectItem value="german">German</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="password" className="space-y-4">
            <Card className="flex items-center">
              <CardHeader>
                <CardTitle className="font-medium text-base">
                  Chat history & training
                </CardTitle>
                <CardDescription className="text-xs">
                  Save new chats on this browser to your history and allow them
                  to be used to improve our models. Unsaved chats will be
                  deleted from our systems within 30 days. This setting does not
                  sync across browsers or devices. Learn more
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Switch id="traindata" />
              </CardContent>
            </Card>
            <Card className="flex items-center">
              <CardHeader className="flex-1">
                <CardTitle className="font-medium text-base">
                  Archive all chat
                </CardTitle>
                <CardDescription className="text-xs">
                  Yorem ipsum dolor sit amet, consectetur adipiscing.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline">Archive all</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
