<?xml version="1.0" encoding="UTF-8"?>
<sc version="201602" id="2" name="" frequency="1" steps="0" defaultIntergreenMatrix="0" interstagesUsingMinDurations="true" checkSum="497716007">
    <signaldisplays>
        <display id="1" name="Red" state="RED">
            <patterns>
                <pattern pattern="MINUS" color="#FF0000" isBold="true"/>
            </patterns>
        </display>
        <display id="2" name="Red/Amber" state="REDAMBER">
            <patterns>
                <pattern pattern="FRAME" color="#CCCC00" isBold="true"/>
                <pattern pattern="SLASH" color="#CC0000" isBold="false"/>
                <pattern pattern="MINUS" color="#CC0000" isBold="false"/>
            </patterns>
        </display>
        <display id="3" name="Green" state="GREEN">
            <patterns>
                <pattern pattern="FRAME" color="#00CC00" isBold="true"/>
                <pattern pattern="SOLID" color="#00CC00" isBold="false"/>
            </patterns>
        </display>
        <display id="4" name="Amber" state="AMBER">
            <patterns>
                <pattern pattern="FRAME" color="#CCCC00" isBold="true"/>
                <pattern pattern="SLASH" color="#CCCC00" isBold="false"/>
            </patterns>
        </display>
    </signaldisplays>
    <signalsequences>
        <signalsequence id="3" name="Red-Red/Amber-Green-Amber">
            <state display="1" isFixedDuration="false" isClosed="true" defaultDuration="1000"/>
            <state display="2" isFixedDuration="true" isClosed="true" defaultDuration="1000"/>
            <state display="3" isFixedDuration="false" isClosed="false" defaultDuration="5000"/>
            <state display="4" isFixedDuration="true" isClosed="true" defaultDuration="3000"/>
        </signalsequence>
    </signalsequences>
    <sgs>
        <sg id="3" name="Signal group 1" defaultSignalSequence="3">
            <defaultDurations>
                <defaultDuration display="1" duration="1000"/>
                <defaultDuration display="2" duration="2000"/>
                <defaultDuration display="3" duration="5000"/>
                <defaultDuration display="4" duration="3000"/>
            </defaultDurations>
        </sg>
        <sg id="4" name="Signal group 2" defaultSignalSequence="3">
            <defaultDurations>
                <defaultDuration display="1" duration="1000"/>
                <defaultDuration display="2" duration="2000"/>
                <defaultDuration display="3" duration="5000"/>
                <defaultDuration display="4" duration="3000"/>
            </defaultDurations>
        </sg>
    </sgs>
    <intergreenmatrices/>
    <progs>
        <prog id="1" cycletime="43000" switchpoint="0" offset="35000" intergreens="0" fitness="0.000000" vehicleCount="0" name="Signal program 1">
            <sgs>
                <sg sg_id="3" signal_sequence="3">
                    <cmds>
                        <cmd display="1" begin="15000"/>
                        <cmd display="3" begin="2000"/>
                    </cmds>
                    <fixedstates>
                        <fixedstate display="2" duration="2000"/>
                        <fixedstate display="4" duration="3000"/>
                    </fixedstates>
                </sg>
                <sg sg_id="4" signal_sequence="3">
                    <cmds>
                        <cmd display="1" begin="0"/>
                        <cmd display="3" begin="17000"/>
                    </cmds>
                    <fixedstates>
                        <fixedstate display="2" duration="2000"/>
                        <fixedstate display="4" duration="3000"/>
                    </fixedstates>
                </sg>
            </sgs>
        </prog>
    </progs>
    <stages/>
    <interstageProgs/>
    <stageProgs/>
    <dailyProgLists/>
</sc>
