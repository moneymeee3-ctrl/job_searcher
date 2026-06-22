"""EMBEDHUNT AI — Interview Question Bank (embedded engineering domain)"""

QUESTIONS: dict[str, list[dict]] = {
    "c": [
        {"q":"Explain the difference between const int* and int* const.","type":"core","difficulty":"medium","expected":"Pointer to const int vs const pointer to int"},
        {"q":"What is volatile keyword and when do you use it in embedded C?","type":"core","difficulty":"medium","expected":"Prevents compiler optimization for hardware registers/ISRs"},
        {"q":"How do you implement a circular buffer in C?","type":"coding","difficulty":"hard","expected":"Array + head/tail indices with wrap-around"},
        {"q":"Explain memory layout of a C program.","type":"core","difficulty":"medium","expected":"Text, data, BSS, heap, stack sections"},
        {"q":"What is the difference between malloc and calloc?","type":"core","difficulty":"easy","expected":"calloc zero-initializes, malloc doesn't"},
    ],
    "c++": [
        {"q":"Explain RAII and why it matters in embedded systems.","type":"core","difficulty":"hard","expected":"Resource Acquisition Is Initialization — deterministic cleanup"},
        {"q":"When would you avoid virtual functions in embedded C++?","type":"core","difficulty":"hard","expected":"vtable overhead, non-deterministic dispatch, ROM usage"},
        {"q":"What are move semantics and how do they differ from copy semantics?","type":"core","difficulty":"medium","expected":"std::move transfers ownership, avoids deep copy"},
    ],
    "rtos": [
        {"q":"What is priority inversion? Give a real-world embedded example.","type":"core","difficulty":"hard","expected":"Low priority task holds mutex needed by high priority — Mars Pathfinder"},
        {"q":"Mutex vs Semaphore vs Event Flag — when to use each?","type":"core","difficulty":"hard","expected":"Mutex=ownership, Semaphore=signaling, Event=conditions"},
        {"q":"How does FreeRTOS implement context switching?","type":"core","difficulty":"hard","expected":"SysTick interrupt, PendSV handler, TCB swap"},
        {"q":"Explain the difference between preemptive and cooperative scheduling.","type":"core","difficulty":"medium","expected":"Preemptive: OS controls, Cooperative: tasks yield"},
        {"q":"What is stack overflow detection in FreeRTOS?","type":"core","difficulty":"medium","expected":"configCHECK_FOR_STACK_OVERFLOW, stack canaries"},
    ],
    "freertos": [
        {"q":"How do you communicate between two FreeRTOS tasks safely?","type":"core","difficulty":"medium","expected":"Queues, Event Groups, Mutexes"},
        {"q":"What is the configTICK_RATE_HZ and how does it affect system behavior?","type":"core","difficulty":"medium","expected":"Controls time resolution and scheduling overhead"},
        {"q":"Explain xTaskCreate parameters.","type":"core","difficulty":"easy","expected":"Function, name, stack size, params, priority, handle"},
    ],
    "autosar": [
        {"q":"What is the difference between AUTOSAR Classic and Adaptive?","type":"core","difficulty":"hard","expected":"Classic: OSEK, fixed config. Adaptive: POSIX, dynamic, service-oriented"},
        {"q":"Explain the RTE (Runtime Environment) in AUTOSAR Classic.","type":"core","difficulty":"hard","expected":"Communication layer between SWCs and BSW"},
        {"q":"What is an ARXML file?","type":"core","difficulty":"medium","expected":"AUTOSAR XML — describes software component interfaces"},
        {"q":"Explain SWC (Software Component) types in AUTOSAR.","type":"core","difficulty":"hard","expected":"Application, Service, Sensor-Actuator, ECU Abstraction, etc."},
    ],
    "can": [
        {"q":"Explain CAN bus arbitration mechanism.","type":"core","difficulty":"hard","expected":"CSMA/CD+AMP — lower ID wins, bit-by-bit dominant/recessive"},
        {"q":"What is the difference between CAN 2.0A and 2.0B?","type":"core","difficulty":"medium","expected":"11-bit vs 29-bit identifier"},
        {"q":"What is CAN FD and what are its advantages?","type":"core","difficulty":"medium","expected":"Flexible Data-rate: up to 8 Mbps, 64 bytes payload"},
        {"q":"Explain UDS (Unified Diagnostic Services) on CAN.","type":"core","difficulty":"hard","expected":"ISO 14229 — diagnostic protocol, service IDs 0x22, 0x27, etc."},
    ],
    "linux kernel": [
        {"q":"What is the difference between kernel space and user space?","type":"core","difficulty":"medium","expected":"Privilege levels, memory protection, syscall interface"},
        {"q":"Explain the Linux device driver model (platform driver, character device).","type":"core","difficulty":"hard","expected":"Platform drivers, file operations, probe/remove lifecycle"},
        {"q":"What is a devicetree and how is it used in embedded Linux?","type":"core","difficulty":"hard","expected":"Hardware description passed to kernel, .dts/.dtb files"},
        {"q":"Explain DMA and why it's important in embedded Linux.","type":"core","difficulty":"hard","expected":"Direct Memory Access bypasses CPU for peripheral data transfer"},
    ],
    "iso 26262": [
        {"q":"What are the ASIL levels and what do they mean?","type":"core","difficulty":"medium","expected":"A-D: severity, exposure, controllability. D = highest integrity"},
        {"q":"Explain the V-model in ISO 26262 context.","type":"core","difficulty":"hard","expected":"Requirements→Architecture→Design→Implementation↑Tests at each level"},
        {"q":"What is HARA (Hazard Analysis and Risk Assessment)?","type":"core","difficulty":"hard","expected":"Identifies hazards, determines ASIL based on S×E×C"},
        {"q":"What is the difference between safety goal and safe state?","type":"core","difficulty":"hard","expected":"Goal: top-level safety requirement. Safe state: system state where no unreasonable risk"},
    ],
    "arm": [
        {"q":"What is the difference between Cortex-M, Cortex-R, and Cortex-A?","type":"core","difficulty":"medium","expected":"M: microcontroller (RTOS), R: real-time, A: application (Linux)"},
        {"q":"Explain NVIC and interrupt priority in Cortex-M.","type":"core","difficulty":"hard","expected":"Nested Vectored Interrupt Controller, priority grouping, preemption"},
        {"q":"What is the MPU (Memory Protection Unit)?","type":"core","difficulty":"hard","expected":"Defines regions with access permissions, enables OS isolation"},
    ],
    "device driver": [
        {"q":"What is the probe() function in a Linux platform driver?","type":"core","difficulty":"hard","expected":"Called when driver matches device, initializes hardware"},
        {"q":"Explain the difference between character device and block device.","type":"core","difficulty":"medium","expected":"Char: byte stream (serial, GPIO). Block: random access (storage)"},
        {"q":"What is devm_* API and why is it preferred?","type":"core","difficulty":"medium","expected":"Device-managed resources, auto-cleanup on driver unbind"},
    ],
    "python": [
        {"q":"How would you use Python for automated embedded testing?","type":"applied","difficulty":"medium","expected":"pyserial, pytest, hardware-in-loop test frameworks"},
        {"q":"Explain GIL and why it matters for embedded Python scripts.","type":"core","difficulty":"medium","expected":"Global Interpreter Lock — limits true parallelism in CPython"},
    ],
    "spi": [
        {"q":"Explain SPI clock polarity (CPOL) and clock phase (CPHA).","type":"core","difficulty":"medium","expected":"CPOL: idle level. CPHA: sampling edge. Modes 0-3"},
        {"q":"What is the maximum SPI speed and what limits it?","type":"core","difficulty":"medium","expected":"Trace length, capacitance, slave max speed"},
    ],
    "i2c": [
        {"q":"What is I2C address collision and how do you resolve it?","type":"core","difficulty":"medium","expected":"Use address variants, external address pins, I2C multiplexer"},
        {"q":"Explain I2C clock stretching.","type":"core","difficulty":"medium","expected":"Slave holds SCL low to pause master — allows slow processing"},
    ],
}

def get_questions_for_skills(skills: list[str], max_per_skill: int = 3) -> dict[str, list[dict]]:
    """Return curated interview questions for matched skills."""
    result = {}
    for skill in skills:
        if skill in QUESTIONS:
            result[skill] = QUESTIONS[skill][:max_per_skill]
    return result

def get_all_questions_flat(skills: list[str]) -> list[dict]:
    """Return flat list of all questions for given skills."""
    flat = []
    for skill in skills:
        for q in QUESTIONS.get(skill, []):
            flat.append({**q, "skill": skill})
    return flat
