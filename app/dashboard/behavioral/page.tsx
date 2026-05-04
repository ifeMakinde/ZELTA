import PageHeader from "@/components/PageHeader";
import { BehavioralDataProvider } from "@/context/BehavioralSnapshotContext";
import Bayse from "./components/bayse";
import Active from "./components/active";
import Decision from "./components/decision";
import Five from "./components/five";
import Weeks from "./components/weeks";
import Zelta from "./components/zelta";

export default function Page() {
  return (
    <BehavioralDataProvider>
      <div>
        <PageHeader
          title="Behavioral Snapshot"
          description="Deep dive into your behavioral bias patterns"
        />

        <Bayse />
        <Active />
        <Decision />
        <Five />
        <Weeks />
        <Zelta />
      </div>
    </BehavioralDataProvider>
  );
}