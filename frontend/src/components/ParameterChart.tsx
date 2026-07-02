import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

interface TrendPoint {
  date: string;
  health_score: number;
}

export default function ParameterChart({ trend }: { trend: TrendPoint[] }) {
  const data = {
    labels: trend.map((t) => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: "Health score",
        data: trend.map((t) => t.health_score),
        borderColor: "#0F766E",
        backgroundColor: "#CCFBF1",
        tension: 0.3,
        pointRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { min: 0, max: 100, ticks: { stepSize: 20 } } },
  };

  if (trend.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-ink/50">
        Upload a report to start tracking your health score over time.
      </div>
    );
  }

  return <Line data={data} options={options} />;
}
