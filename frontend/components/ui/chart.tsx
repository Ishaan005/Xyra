"use client"

import { Bar, Line } from "react-chartjs-2"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  PointElement,
  LineElement,
  Filler,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, ChartTooltip, Legend, PointElement, LineElement, Filler)

interface BarChartProps {
  data: any
  options: any
  className?: string
}

export function BarChart({ data, options, className }: BarChartProps) {
  return (
    <div className={className}>
      <Bar data={data} options={options} />
    </div>
  )
}

interface LineChartProps {
  data: any
  options: any
  className?: string
}

export function LineChart({ data, options, className }: LineChartProps) {
  return (
    <div className={className}>
      <Line data={data} options={options} />
    </div>
  )
}
