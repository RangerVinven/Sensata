import { useState, useEffect } from "react"
import { LineChart, Line, Legend, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

function LineChartComponent(props: any) {

    const [pastSevenDaysTraffic, setPastSevenDaysTraffic] = useState(props.pastSevenDaysTraffic); // The raw past 7 days traffic
    const [weeklyTraffic, setWeeklyTraffic] = useState<Array<WeekDayData> | null>(null) // The formatted traffic from the past 7 days

    type WeekDayData = {
        day: string,
        Traffic: number
    }

    type WeekDays = {
        Mon: number,
        Tue: number,
        Wed: number,
        Thu: number,
        Fri: number,
        Sat: number,
        Sun: number
    }

    type SensorData = {
        time_added: string,
        sensor_id_sensor_table: Number,
        time_recorded: string,
        sensor_data_id: Number,
        unique_id: string,
        data: string
    }

    // Converts the numbers 0-6 to "Mon" - "Sun"
    function convertDayToDayName(day: number) : string {
        if (day > 6 || day < 0) throw new Error("Number must be between 0 and 6");

        switch(day) {
            case 0:
                return "Sun"
            case 1:
                return "Mon"
            case 2:
                return "Tue"
            case 3:
                return "Wed"
            case 4:
                return "Thu"
            case 5:
                return "Fri"
            case 6:
                return "Sat"
        }

        return "";
    }

    // Adds the missing days where there wasn't traffic, to the given object
    function addRestOfDaysToArray(days: WeekDays) {
        const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for (let i = 0; i < weekDays.length; i++) {
            if (!(weekDays[i] in days)) {
                days[weekDays[i] as keyof WeekDays] = 0;
            }
        }

        return days;
    }

    function convertDayToNumber(day: string) {
        switch(day) {
            case "Sun":
                return 0
            case "Mon":
                return 1
            case "Tue":
                return 2
            case "Wed":
                return 3
            case "Thu":
                return 4
            case "Fri":
                return 5
            case "Sat":
                return 6

        }
        return 1
    }

    function recordToWeekDay(record: SensorData) {
        return new Date(record.time_recorded).toLocaleString("en-GB", { weekday: "short" })
    }

    function parseTraffic(traffic: Array<SensorData>) {

        // let trafficPerDay: any = {}
        //
        // // Loops over the traffic
        // for (let i = 0; i < traffic.length; i++) {
        //     const time_recorded = new Date(traffic[i].time_recorded);
        //     const time_day = time_recorded.getDay() // Returns 0-6 ("Sunday"-"Saturday")
        //
        //     // Adds the day to the trafficPerDay
        //     if(convertDayToDayName(time_day) in trafficPerDay) {
        //         trafficPerDay[convertDayToDayName(time_day)] += 1;
        //     } else {
        //         trafficPerDay[convertDayToDayName(time_day)] = 1;
        //     }
        // }
        //
        //
        // // Adds the remaning days and sets them to 0
        // // trafficPerDay = addRestOfDaysToArray(trafficPerDay);
        //
        // // Turns the traffic into an array of objects
        // let weeklyActivityArray = [];
        // for(let key in trafficPerDay) {
        //     weeklyActivityArray.push({
        //         day: key,
        //         "Traffic": trafficPerDay[key]
        //     })
        // }
        //
        //
        // const daysOrder = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        // weeklyActivityArray.sort((a: any, b: any) => daysOrder.indexOf(a.day) - daysOrder.indexOf(b.day));
        //
        // setWeeklyTraffic(weeklyActivityArray)
        //



        
        // Sorts the traffic from earliest to latest
        const sorted_traffic = traffic.sort((a, b) => new Date(a.time_recorded).getTime() - new Date(b.time_recorded).getTime());
       
        let week_activity: Array<WeekDayData> = [];
        let each_days_traffic: WeekDays = {
            Mon: 0,
            Tue: 0,
            Wed: 0,
            Thu: 0,
            Fri: 0,
            Sat: 0,
            Sun: 0
        }
         
        // Counts how much traffic is in each day
        sorted_traffic.forEach(record => {
             // Gets the day the traffic is on
            const day = recordToWeekDay(record)
            each_days_traffic[day as keyof WeekDays] += 1
        })

        // Finds out the earliest day
        const earliest_day = recordToWeekDay(sorted_traffic[0]);
        
        // The days of the week
        const week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        const week_day_index = week_days.indexOf(earliest_day);

        // Gets the correct order to display the day in on the graph
        // The chart displays the last 7 days' data, this finds what
        // order the days should be shown

        // Sets next_day to (week_day_index + 1) unless it's 7, then sets it to 0
        let next_day = week_day_index !== 7 ? week_day_index + 1 : 0
        let order_of_days = []

        // Loops and adds the next day onto the order_of_days array
        for (let i = 0; i < 6; i++) {
            order_of_days.push(week_days[next_day]);
            next_day += 1;

            if(next_day === 7) next_day = 0
        }

        
        // Loops and adds the day and its amount of traffic to the week_activity array
        for (let i = 0; i < order_of_days.length; i++) {
            week_activity.push({
                day: order_of_days[i],
                Traffic: each_days_traffic[order_of_days[i] as keyof WeekDays]
            })
        }

        setWeeklyTraffic(week_activity);
   }

    useEffect(() => {
        parseTraffic(pastSevenDaysTraffic)
    }, [])


    if (weeklyTraffic == null) {
        return <h3>Loading...</h3>
    } else {
        return <ResponsiveContainer height={"100%"} width={"100%"}>
            <LineChart data={weeklyTraffic}>
               <CartesianGrid />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line dataKey="Traffic" fill="#BF40BF" />
            </LineChart>
        </ResponsiveContainer>
    }
}

export default LineChartComponent;
