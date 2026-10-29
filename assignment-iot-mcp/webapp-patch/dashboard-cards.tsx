// คัดลอกไป webapp/src/components/dashboard-cards.tsx แล้ว import ไปวางใน pages/index.tsx:
//   import { DashboardCards } from "@/components/dashboard-cards";
//   ... <DashboardCards />   (เหนือกราฟเดิม)
// และเปิดใช้ useSensorWs() ใน index.tsx (บรรทัดที่ comment ไว้) เพื่ออัปเดตสด
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

type SensorData = {
  id: number;
  sensorName: string;
  sensorType: string;
  value: number;
  unit: string | null;
  timestamp: number;
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { Authorization: `Bearer ${import.meta.env.VITE_API_SECRET}` },
});

const CARDS = [
  { type: "temperature", label: "Temperature", unit: "°C" },
  { type: "humidity", label: "Humidity", unit: "%" },
  { type: "distance", label: "Distance", unit: "cm" },
];

export function DashboardCards() {
  const queryClient = useQueryClient();

  const sensors = useQuery({
    queryKey: ["sensors"],
    queryFn: async () => (await api.get<SensorData[]>("sensors")).data,
    refetchInterval: 5000,
  });

  const led = useQuery({
    queryKey: ["led"],
    queryFn: async () => (await api.get<{ state: string }>("devices/led")).data,
    refetchInterval: 2000,
  });

  const toggle = useMutation({
    mutationFn: (action: "on" | "off") => api.post("devices/led", { action }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["led"] }),
  });

  // ค่าล่าสุดของแต่ละชนิด (id มากสุด)
  const latest = (type: string) =>
    (sensors.data ?? [])
      .filter((s) => s.sensorType === type)
      .sort((a, b) => b.id - a.id)[0];

  const isOn = led.data?.state === "ON";

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {CARDS.map((c) => {
        const row = latest(c.type);
        return (
          <Card key={c.type}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">{c.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {row ? `${row.value.toFixed(1)} ${c.unit}` : "-"}
              </div>
              <div className="text-xs text-muted-foreground">{row?.sensorName ?? ""}</div>
            </CardContent>
          </Card>
        );
      })}

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">LED</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-3">
          <span className="text-2xl font-bold">{led.data?.state ?? "-"}</span>
          <Button
            size="sm"
            variant={isOn ? "outline" : "default"}
            disabled={toggle.isPending}
            onClick={() => toggle.mutate(isOn ? "off" : "on")}
          >
            {isOn ? "Turn off" : "Turn on"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
