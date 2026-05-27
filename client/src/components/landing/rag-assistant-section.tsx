'use client';

import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

export default function RAGAssistant() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });

  return (
    <section id="rag" ref={ref} className="relative w-full overflow-hidden">
      <div className="flex flex-col md:flex-row min-h-[600px] md:min-h-[700px]">

        {/* Left Half */}
        <motion.div
          initial={{ opacity: 0, x: -40 }}
          animate={inView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="relative w-full md:w-1/2 bg-yefai-dark-charcoal overflow-hidden"
        >
          {/* Cyan ambient glow */}
          <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-cyan-500/[0.04] rounded-full blur-[120px]" />

          {/* Image */}
          <div className="absolute inset-0 flex items-end">
            <img
              src="https://readdy.ai/api/search-image?query=AI conversational assistant interface for industrial factory, dark chat UI with glowing cyan message bubbles and holographic data overlays, manufacturing diagnostics conversation, futuristic dark mode interface design, premium tech aesthetic&width=800&height=900&seq=14&orientation=portrait"
              alt="RAG Assistant Interface"
              className="w-full h-full object-cover object-top opacity-80"
            />
          </div>

          {/* Gradient left-to-right */}
          <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/30 to-transparent" />

          {/* Gradient bottom-to-top */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40" />

          {/* Content overlay */}
          <div className="relative z-10 h-full flex flex-col justify-end p-8 md:p-12 lg:p-16">
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-xs tracking-[0.2em] uppercase text-cyan-400/70 font-medium mb-4"
            >
              Diyaloğa Dayalı Zeka
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: 0.4 }}
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-[1.05]"
            >
              Fabrikanıza<br />Soru<br />Sorun.
            </motion.h2>
          </div>
        </motion.div>

        {/* Right Half */}
        <motion.div
          initial={{ opacity: 0, x: 40 }}
          animate={inView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative w-full md:w-1/2 bg-yefai-black flex flex-col items-center justify-center p-8 md:p-12 lg:p-20 text-center"
        >
          {/* Violet ambient glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-violet-500/[0.02] rounded-full blur-[120px]" />

          <div className="relative z-10 max-w-md">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight">
              RAG Asistanını<br />Devreye Alın.
            </h2>
            <p className="mt-6 text-base md:text-lg text-white/35 font-light leading-relaxed">
              Tüm tesis geçmişiniz, kılavuzlar, sensör kayıtları ve bakım kayıtları — doğal dil aracılığıyla erişilebilir. Bir iş milinin neden titrediğini sorun. Değişimin ne zaman planlanacağını sorun. Mart kesintisinde ne olduğunu sorun. Fabrikanız cevaplasın.
            </p>
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mt-10 inline-flex items-center gap-3 px-8 py-4 rounded-full bg-yefai-charcoal border border-white/[0.08] text-white font-medium text-sm hover:bg-white/[0.08] hover:border-cyan-400/20 transition-all duration-300 cursor-pointer group"
            >
              <span>Erişim Talep Et</span>
              <i className="ri-arrow-right-line text-cyan-400 group-hover:translate-x-1 transition-transform" />
            </motion.button>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
