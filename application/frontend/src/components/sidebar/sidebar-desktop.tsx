import { ChatHistory } from "./chat-history";
import { Sidebar } from "./sidebar";

export async function SidebarDesktop() {
  return (
    <Sidebar className="peer absolute inset-y-0 z-30 bg-card hidden -translate-x-full border-r duration-300 ease-in-out data-[state=open]:translate-x-0 lg:flex lg:w-[250px] xl:w-[300px]">
      <ChatHistory />
    </Sidebar>
  );
}
