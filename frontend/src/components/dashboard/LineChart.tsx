import { LineChart, Line, Legend, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

function LineChartComponent() {

    const weeklyActivity = [
  { day: "Mon", "Traffic": 120 },
  { day: "Tue", "Traffic": 200 },
  { day: "Wed", "Traffic": 150 },
  { day: "Thu", "Traffic": 170 },
  { day: "Fri", "Traffic": 180 },
  { day: "Sat", "Traffic": 220 },
  { day: "Sun", "Traffic": 240 }
];

    return (
        <ResponsiveContainer height={"100%"} width={"100%"}>
            <LineChart data={weeklyActivity}>
                <CartesianGrid />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line dataKey="Traffic" fill="#BF40BF" />
            </LineChart>
        </ResponsiveContainer>
    )
}

export default LineChartComponent;
