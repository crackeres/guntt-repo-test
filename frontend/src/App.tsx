import type { FC } from "react";
import GunttChart from "./components/widgets/guntt-chart";
import "./index.css";

const App: FC = () => {
  return (
    <div>
      <div className="text-3xl font-bold">
        <GunttChart />
      </div>
    </div>
  );
};

export default App;