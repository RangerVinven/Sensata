import { Legend, BarChart, Bar, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

function BarChartComponent() {

    const hourlyData = [
      { "name": "12am", "Traffic": 120 },
      { "name": "1am", "Traffic": 90 },
      { "name": "2am", "Traffic": 75 },
      { "name": "3am", "Traffic": 60 },
      { "name": "4am", "Traffic": 50 },
      { "name": "5am", "Traffic": 45 },
      { "name": "6am", "Traffic": 70 },
      { "name": "7am", "Traffic": 85 },
      { "name": "8am", "Traffic": 100 },
      { "name": "9am", "Traffic": 150 },
      { "name": "10am", "Traffic": 180 },
      { "name": "11am", "Traffic": 200 },
      { "name": "12pm", "Traffic": 220 },
      { "name": "1pm", "Traffic": 210 },
      { "name": "2pm", "Traffic": 230 },
      { "name": "3pm", "Traffic": 240 },
      { "name": "4pm", "Traffic": 250 },
      { "name": "5pm", "Traffic": 260 },
      { "name": "6pm", "Traffic": 270 },
      { "name": "7pm", "Traffic": 260 },
      { "name": "8pm", "Traffic": 240 },
      { "name": "9pm", "Traffic": 220 },
      { "name": "10pm", "Traffic": 190 },
      { "name": "11pm", "Traffic": 160 }
    ];

    return (
        <ResponsiveContainer height={"100%"} width={"100%"}>
            <BarChart data={hourlyData}>
                <CartesianGrid />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Traffic" fill="#BF40BF" />
            </BarChart>
        </ResponsiveContainer>
    )
}

export default BarChartComponent;
