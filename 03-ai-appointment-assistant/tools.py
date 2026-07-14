TOOLS = [
    {
        "type": "function",
        "name": "get_available_slots",
        "description": (
            "Get the available appointment times for a specific date. "
            "Use this when the user asks which times are free."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format.",
                }
            },
            "required": ["date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
   {
       "type": "function",
       "name": "create_appointment",
       "description": (
           "Create a new appointment for a user. "
           "Use this when the user clearly asks to book an appointment."
       ),
       "parameters": {
           "type": "object",
           "properties": {
               "name": {
                   "type": "string",
                   "description": "The name of the person booking the appointment.",
               },
               "date": {
                   "type": "string",
                   "description": "The appointment date in YYYY-MM-DD format.",
               },
               "time": {
                   "type": "string",
                   "description": "The appointment time in HH:MM format.",
               },
           },
           "required": ["name", "date", "time"],
           "additionalProperties": False,
       },
       "strict": True,
   },
   {
       "type": "function",
       "name": "cancel_appointment",
       "description": (
           "Cancel an existing appointment using its appointment ID. "
           "Use this when the user asks to cancel an appointment and provides the ID."
       ),
       "parameters": {
           "type": "object",
           "properties": {
               "appointment_id": {
                   "type": "string",
                   "description": "The unique ID of the appointment to cancel.",
               }
           },
           "required": ["appointment_id"],
           "additionalProperties": False,
       },
       "strict": True,
   },
   {
       "type": "function",
       "name": "list_appointments",
       "description": (
           "List all appointments, including their IDs, dates, times, names, and statuses. "
           "Use this when the user asks to see their appointments."
       ),
       "parameters": {
           "type": "object",
           "properties": {},
           "required": [],
           "additionalProperties": False,
       },
       "strict": True,
   },
   {
       "type": "function",
       "name": "update_appointment",
       "description": (
           "Update the date and time of an existing appointment. "
           "Use this when the user wants to move or reschedule an appointment."
       ),
       "parameters": {
           "type": "object",
           "properties": {
               "appointment_id": {
                   "type": "string",
                   "description": "The unique ID of the appointment.",
               },
               "new_date": {
                   "type": "string",
                   "description": "The new date in YYYY-MM-DD format.",
               },
               "new_time": {
                   "type": "string",
                   "description": "The new time in HH:MM format.",
               },
           },
           "required": [
               "appointment_id",
               "new_date",
               "new_time",
           ],
           "additionalProperties": False,
       },
       "strict": True,
   }
]