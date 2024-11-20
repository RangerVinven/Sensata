import SensorType from "../../assets/SensorType.tsx";

type Props = {
    sensors: Array<SensorType> | null,
    setIsLoading: Function
}

// The select menu for the sensors
function SensorSelect(props: Props) {

    return <>
        <select className="dropdown">
            <option value="" disabled selected>Select a sensor</option>
            {
                props.sensors?.map((sensor, index) => {
                    return <option value={ sensor.sensor_model_name } selected={index === 0}>{ sensor.sensor_model_name }</option>
                })
            }
        </select>
    </>
}

export default SensorSelect; 

