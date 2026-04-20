import { useState } from "react";
import axios from "axios";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import { VITE_API_URL } from "../config";

type Point = {
  id: string;
  filename: string;
  type: string;
  x: number;
  y: number;
};

type Props = {
  onSelect?: (item: any) => void;
};

const COLORS: Record<string, string> = {
  image: "#2196f3",
  audio: "#9c27b0",
  pdf: "#f44336",
  other: "#777",
};

function getTypeKey(type: string): keyof typeof COLORS {
  if (type.includes("image")) return "image";
  if (type.includes("audio")) return "audio";
  if (type.includes("pdf")) return "pdf";
  return "other";
}

export default function EmbeddingPlot({ onSelect }: Props) {
  const [points, setPoints] = useState<Point[]>([]);

  const loadData = async () => {
    const res = await axios.get<Point[]>(`${VITE_API_URL}/visualise`);
    setPoints(res.data);
  };

  // group points by type for colouring
  const grouped = {
    image: points.filter(p => p.type.includes("image")),
    audio: points.filter(p => p.type.includes("audio")),
    pdf: points.filter(p => p.type.includes("pdf")),
    other: points.filter(
      p =>
        !p.type.includes("image") &&
        !p.type.includes("audio") &&
        !p.type.includes("pdf")
    ),
  };

  return (
    <div style={{ padding: 20 }}>
      <h3>Embedding Visualisation (t-SNE)</h3>

      <button onClick={loadData}>Load Visualisation</button>

      <ScatterChart width={1200} height={900}>
        <XAxis dataKey="x" name="X" />
        <YAxis dataKey="y" name="Y" />

        <Tooltip
          content={({ payload }) => {
            if (!payload || payload.length === 0) return null;

            const p = payload[0].payload;

            return (
              <div
                style={{
                  background: "#fff",
                  padding: "6px 10px",
                  border: "1px solid #ccc",
                  borderRadius: 6,
                  fontSize: 12,
                }}
              >
                <strong>{p.filename}</strong>
                <br />
                <span style={{ color: "#666" }}>{p.type}</span>
              </div>
            );
          }}
        />

        <Legend />

        <Scatter
          name="Images"
          data={grouped.image}
          fill={COLORS.image}
          onClick={(data: any) => onSelect?.(data)}
        />
        <Scatter
          name="Audio"
          data={grouped.audio}
          fill={COLORS.audio}
          onClick={(data: any) => onSelect?.(data)}
        />
        <Scatter
          name="PDF"
          data={grouped.pdf}
          fill={COLORS.pdf}
          onClick={(data: any) => onSelect?.(data)}
        />
        <Scatter
          name="Other"
          data={grouped.other}
          fill={COLORS.other}
          onClick={(data: any) => onSelect?.(data)}
        />
      </ScatterChart>
    </div>
  );
}