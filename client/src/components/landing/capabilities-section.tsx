'use client';

import { useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const capabilities = [
  {
    title: 'Anomaly Detection',
    description:
      'Real-time sub-millisecond anomaly detection across every sensor stream. Identifies deviations before they propagate.',
    image:
      'https://readdy.ai/api/search-image?query=Close-up of industrial CNC machine sensors and monitoring equipment with glowing cyan LED indicators in a dark high-tech factory environment, cinematic lighting, dark background with subtle grid lines, ultra-premium manufacturing aesthetic&width=600&height=800&seq=1&orientation=portrait',
    status: 'LIVE',
  },
  {
    title: 'Wear Prediction',
    description:
      'Predictive modeling that forecasts tool degradation, surface finish decay, and optimal replacement windows.',
    image:
      'https://readdy.ai/api/search-image?query=Macro photography of precision cutting tool tip with microscopic wear patterns visible, dark industrial background with cyan and violet accent lighting, ultra sharp detail, premium manufacturing aesthetic, cinematic depth of field&width=600&height=800&seq=2&orientation=portrait',
    status: 'PREDICTIVE',
  },
  {
    title: 'Crisis Scoring',
    description:
      'Intelligent spare-parts inventory scoring that predicts supply-chain disruptions and flags critical shortage risks.',
    image:
      'https://readdy.ai/api/search-image?query=Industrial crisis management dashboard interface with glowing red and amber alert indicators on dark background, holographic data overlays, supply chain visualization nodes connected by light lines, premium dark UI aesthetic&width=600&height=800&seq=3&orientation=portrait',
    status: 'CRITICAL',
  },
];

export default function Capabilities() {
  const [activeIndex, setActiveIndex] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <section
      id="capabilities"
      ref={ref}
      className="relative w-full py-28 md:py-36 bg-yefai-black overflow-hidden"
    >
      {/* Grid background */}
      <div className="absolute inset-0 grid-bg opacity-15" />

      {/* Ambient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cyan-500/[0.015] rounded-full blur-[150px]" />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="mb-16 md:mb-20"
        >
          <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white leading-tight">
            Platform Capabilities
            <span className="inline-block ml-3 text-cyan-400 text-2xl md:text-4xl align-middle">
              <i className="ri-focus-3-line" />
            </span>
          </h2>
          <p className="mt-4 text-base md:text-lg text-white/35 max-w-xl font-light">
            Three core pillars of autonomous manufacturing intelligence. Each deployed at machine speed, each trained on industrial-scale telemetry.
          </p>
        </motion.div>

        {/* Cards */}
        <div className="flex flex-col md:flex-row gap-4 md:gap-5">
          {capabilities.map((cap, index) => {
            const isActive = activeIndex === index;
            return (
              <motion.div
                key={cap.title}
                initial={{ opacity: 0, y: 40 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.15 * index }}
                onMouseEnter={() => setActiveIndex(index)}
                className={`relative rounded-2xl overflow-hidden cursor-pointer transition-all duration-700 ease-out ${
                  isActive ? 'md:flex-[2]' : 'md:flex-1'
                }`}
                style={{ minHeight: '420px' }}
              >
                {/* Background image */}
                <div className="absolute inset-0">
                  <img
                    src={cap.image}
                    alt={cap.title}
                    className="w-full h-full object-cover transition-transform duration-700 ease-out"
                    style={{ transform: isActive ? 'scale(1.05)' : 'scale(1)' }}
                  />
                </div>

                {/* Gradient overlay 1 */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

                {/* Gradient overlay 2 */}
                <div className="absolute inset-0 bg-gradient-to-r from-black/30 to-transparent" />

                {/* Status badge */}
                <div className="absolute top-5 right-5 z-20">
                  <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] tracking-widest uppercase font-semibold border backdrop-blur-sm ${
                      cap.status === 'LIVE'
                        ? 'bg-emerald-500/10 border-emerald-400/30 text-emerald-400'
                        : cap.status === 'PREDICTIVE'
                        ? 'bg-cyan-500/10 border-cyan-400/30 text-cyan-400'
                        : 'bg-amber-500/10 border-amber-400/30 text-amber-400'
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        cap.status === 'LIVE'
                          ? 'bg-emerald-400 animate-pulse'
                          : cap.status === 'PREDICTIVE'
                          ? 'bg-cyan-400 animate-pulse'
                          : 'bg-amber-400 animate-pulse'
                      }`}
                    />
                    {cap.status}
                  </span>
                </div>

                {/* Content */}
                <div className="absolute bottom-0 left-0 right-0 p-6 md:p-8 z-20">
                  <h3
                    className={`font-bold text-white transition-all duration-500 ${
                      isActive ? 'text-2xl md:text-3xl' : 'text-xl md:text-2xl'
                    }`}
                  >
                    {cap.title}
                  </h3>
                  <motion.p
                    initial={false}
                    animate={{ opacity: isActive ? 1 : 0.5, height: isActive ? 'auto' : '48px' }}
                    className="mt-3 text-sm md:text-base text-white/50 font-light leading-relaxed overflow-hidden"
                  >
                    {cap.description}
                  </motion.p>
                  {isActive && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4 }}
                      className="mt-5 flex items-center gap-2"
                    >
                      <span className="text-sm font-medium text-cyan-400">Learn more</span>
                      <i className="ri-arrow-right-line text-cyan-400 text-sm" />
                    </motion.div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
