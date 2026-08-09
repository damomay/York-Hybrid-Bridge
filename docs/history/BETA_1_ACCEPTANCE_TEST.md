# Climate Bridge Beta.1 Acceptance Test

This is the single end-to-end acceptance test for the first York unit. Every
Home Assistant step below was checked against the Beta.1 production allowlists.

The required starting state is Power On / Cool / 22.5 °C / Fan High / Swing
Off. Both louvers must be stationary.

1. Home Assistant: Fan High → Low.
2. Home Assistant: 22.5 → 20.5 °C. Fan Low must remain.
3. Home Assistant: Power Off.
4. Home Assistant: Power On in Cool. The retained 20.5 °C / Fan Low / Swing Off
   shape must return.
5. Home Assistant: Cool → Heat. Fan Low, 20.5 °C and Swing Off must remain.
6. Home Assistant: Heat → Cool. Fan Low, 20.5 °C and Swing Off must remain.
7. Home Assistant: 20.5 → 22.5 °C. Fan Low must remain.
8. Home Assistant: Fan Low → High.

Wait at least 40 seconds after each command and require formal verification,
four UDP sends and zero retries before continuing. The unit must remain on
except during the intentional Power Off step; the display must match; and both
louvers must remain stationary.

Stop immediately on a rejection, retry, failed verification, unexpected power,
fan or swing change, or louver movement. Capture one continuous log and Home
Assistant screenshots after steps 2, 4, 6 and 8.
