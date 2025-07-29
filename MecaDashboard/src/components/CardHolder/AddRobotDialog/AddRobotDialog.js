import React from 'react'
import styles from './AddRobotDialog.module.css'
import { useState } from 'react'

export default function AddRobotDialog(props) {
    const [inputName, setInputName] = useState('Meca500')
    const [inputIp, setInputIp] = useState('192.168.0.100')


    return (
        <div className={styles.dialogbox}>
            <h1 className={styles.title}>Add a robot</h1>
            <div className={styles.userinput}>
                <label htmlFor='ipadd'>Robot Name: </label>
                <input type='text' name='name' id='robotname' value={inputName} onInput={e => setInputName(e.target.value)}></input><br></br>
            </div>
            <div className={styles.userinput}>
                <label htmlFor='ipadd'>IP Address: </label>
                <input type='text' name='ipadd' id='ipadd' value={inputIp} onInput={e => setInputIp(e.target.value)}></input><br></br>
            </div>
            <div>
                <button className={styles.dialogbutton} onClick={() => props.createRobotHandle(inputName, inputIp)}>Add robot</button>
                <button className={styles.dialogbutton} onClick={props.closeDialogHandle}>Cancel</button>
            </div>

        </div>
    )
}
