import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "./ui/label";

function SatisfiedOption() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          😊 Very Satisfied
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            Great! Would you like to share what you liked the most?
          </DialogTitle>
          <DialogDescription>Select all that apply. </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="flex flex-col items-start w-fit gap-4">
            <Button variant="outline" size="sm">
              Response speed
            </Button>
            <Button variant="outline" size="sm">
              Accuracy of information
            </Button>
            <Button variant="outline" size="sm">
              Interaction felt impersonal or robotic
            </Button>
          </div>

          <div className="grid grid-cols-2 items-center gap-2">
            <Label htmlFor="username" className="text-left">
              How can the response be improved? (optional)
            </Label>
            <Input
              id="username"
              placeholder="Your feedback..."
              className="col-span-3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Submit</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function SomewhatSatisfiedOption() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          😊 Very Satisfied
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>What aspects of the service met your needs?</DialogTitle>
          <DialogDescription>Select all that apply. </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="flex flex-col items-start w-fit gap-4">
            <Button variant="outline" size="sm">
              Responses were too slow
            </Button>
            <Button variant="outline" size="sm">
              Did not find what I was looking for
            </Button>
            <Button variant="outline" size="sm">
              Did not find what I was looking for
            </Button>
          </div>
          <div className="grid grid-cols-2 items-center gap-2">
            <Label htmlFor="username" className="text-left">
              How can the response be improved? (optional)
            </Label>
            <Input
              id="username"
              placeholder="Your feedback..."
              className="col-span-3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Submit</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function NotSatisfiedOption() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          😊 Very Satisfied
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            Great! Would you like to share what you liked the most?
          </DialogTitle>
          <DialogDescription>Select all that apply. </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="flex flex-col items-start w-fit gap-4">
            <Button variant="outline" size="sm">
              The clarity of the information provided
            </Button>
            <Button variant="outline" size="sm">
              The comprehensive coverage of topics
            </Button>
            <Button variant="outline" size="sm">
              The speed of the response
            </Button>
          </div>
          <div className="grid grid-cols-2 items-center gap-2">
            <Label htmlFor="username" className="text-left">
              Other (please specify)
            </Label>
            <Input
              id="username"
              placeholder="Your feedback..."
              className="col-span-3"
            />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Submit</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function ChatFeedback() {
  return (
    <div className="flex sm:pb-8 pb-16">
      <Card className="absolute w-full mx-auto">
        <CardContent className="flex flex-row items-center justify-center h-full py-4">
          <span className="text-sm font-medium text-center whitespace-nowrap mr-2">
            Did we resolve your issue today?
          </span>
          <div className="flex items-center gap-2 justify-center">
            <SatisfiedOption />
            <SomewhatSatisfiedOption />
            <NotSatisfiedOption />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
