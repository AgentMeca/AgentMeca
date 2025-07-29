import React, { useState, useEffect, useRef } from 'react'
import StatusLed from './StatusLed/StatusLed'
import styles from './StatusBar.module.css'

export default function StatusBar(props) {
    const [robotState, setRobotState] = useState({
        "Connection": false,
        "Activated": false,
        "Homed": false,
        "Error": false,
    })
    const isMounted = useRef(false)

    useEffect(() => {
        if (isMounted.current) {

            setRobotState({
                ...robotState,
                "Connection": !robotState["Connection"]
            })
        } else {
            isMounted.current = true
        }

    }, [props.buttonState])


    var connectioncolor = robotState.Connection ? 'ledgreen' : 'ledgrey'

    return (
        <div className={styles.StatusBar}>
            <div>
                <div className={styles.labels}><span className={styles.label}>Connection</span><StatusLed bgcolor={props.robotState.Connection ? 'ledgreen' : 'ledgrey'} /></div>
                <div className={styles.labels}><span className={styles.label}>Activated</span><StatusLed bgcolor={props.robotState.Activated ? 'ledgreen' : 'ledgrey'} /></div>
            </div>
            <div>
                <div className={styles.labels}><span className={styles.label}>Homed</span><StatusLed bgcolor={props.robotState.Homed ? 'ledgreen' : 'ledgrey'} /></div>
                <div className={styles.labels}><span className={styles.label}>Error</span><StatusLed bgcolor={props.robotState.Error ? 'ledred' : 'ledgrey'} /></div>
            </div>
        </div>
    )
}
