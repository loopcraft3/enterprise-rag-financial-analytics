import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const STEPS = [
    "Searching your documents…",
    "Reading the relevant pages…",
    "Checking the numbers…",
    "Writing your answer…",
];

function Thinking() {
    const [step, setStep] = useState(0);
    const [slow, setSlow] = useState(false);

    useEffect(() => {
        const a = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 2200);
        // The free server sleeps when nobody uses it; the first question can take a minute.
        const b = setTimeout(() => setSlow(true), 9000);
        return () => {
            clearInterval(a);
            clearTimeout(b);
        };
    }, []);

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="flex items-start gap-3"
        >
            <div className="orb orb-think h-8 w-8 shrink-0 mt-0.5" />
            <div>
                <motion.p
                    key={step}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-[15px] text-muted"
                >
                    {STEPS[step]}
                </motion.p>
                <div className="flex gap-1.5 mt-2">
                    {[0, 1, 2].map((i) => (
                        <span
                            key={i}
                            className="h-1.5 w-1.5 rounded-full bg-accent/60 animate-bounce"
                            style={{ animationDelay: `${i * 0.15}s` }}
                        />
                    ))}
                </div>
                {slow && (
                    <p className="text-xs text-muted/80 mt-3 max-w-xs">
                        Waking up the free server. The first question can take up to a minute.
                    </p>
                )}
            </div>
        </motion.div>
    );
}

export default Thinking;
