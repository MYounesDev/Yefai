'use client';

import { useRef, useState } from 'react';
import { motion, useInView } from 'framer-motion';

const dashboards = [
  {
    title: 'Canlı Telemetri',
    subtitle:
      'Tüm aktif ünitelerde gerçek zamanlı iş mili sıcaklık, titreşim ve yük izleme.',
    image:
      'https://readdy.ai/api/search-image?query=Industrial telemetry dashboard UI with real-time sensor data charts in dark mode, glowing cyan line graphs and gauges on deep navy background, premium futuristic manufacturing control panel aesthetic, holographic data overlays&width=700&height=500&seq=4&orientation=landscape',
    status: 'CANLI',
  },
  {
    title: 'Kestirimci Analitik',
    subtitle:
      'Güven aralıkları ve değiştirme planlamasıyla aşınma yörüngesi modellemesi.',
    image:
      'https://readdy.ai/api/search-image?query=Predictive analytics dashboard with forecast curves and probability charts in dark futuristic UI, violet and cyan gradient data visualization, manufacturing intelligence platform interface, deep navy background&width=700&height=500&seq=5&orientation=landscape',
    status: 'KESTİRİMCİ',
  },
  {
    title: 'Takım Aşınma İzleyicisi',
    subtitle:
      'Otomatik uyarı eşikleri ve aşınma oranı puanlamasıyla mikroskobik bozulma takibi.',
    image:
      'https://readdy.ai/api/search-image?query=Tool wear monitoring dashboard with microscopic surface analysis visualization, dark industrial UI with amber and red alert zones, precision manufacturing quality control interface, futuristic dark mode design&width=700&height=500&seq=6&orientation=landscape',
    status: 'KRİTİK',
  },
  {
    title: 'Kriz Genel Bakış',
    subtitle:
      'Tedarik zinciri kesinti puanlaması, envanter boşlukları ve acil tedarik süreci.',
    image:
      'https://readdy.ai/api/search-image?query=Crisis management dashboard with supply chain network map visualization, red alert indicators on dark background, inventory shortage warnings, industrial operations command center UI, premium dark theme&width=700&height=500&seq=7&orientation=landscape',
    status: 'KRİTİK',
  },
];

export default function DashboardPreview() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const sectionRef = useRef(null);
  const inView = useInView(sectionRef, { once: true, margin: '-80px' });
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  function checkScroll() {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 10);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  }

  function scroll(dir: 'left' | 'right') {
    if (scrollRef.current) {
      const amount = scrollRef.current.clientWidth * 0.8;
      scrollRef.current.scrollBy({ left: dir === 'left' ? -amount : amount, behavior: 'smooth' });
      setTimeout(checkScroll, 400);
    }
  }

  return (
    <section
      id="dashboard"
      ref={sectionRef}
      className="relative w-full py-28 md:py-36 bg-yefai-navy overflow-hidden"
    >
      <div className="absolute inset-0 grid-bg opacity-15" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 md:px-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.7 }}
          className="flex flex-col md:flex-row md:items-end justify-between mb-12 md:mb-16 gap-4"
        >
          <div>
            <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white leading-tight">
              Yönetim Paneli Önizlemesi
            </h2>
          </div>
          <p className="text-sm md:text-base text-white/35 font-light max-w-sm">
            Gerçek zamanlı tesis telemetrisi ve kontrolü — her metrik, her uyarı, her karar yüzeyi.
          </p>
        </motion.div>

        {/* Scroll area */}
        <div className="relative">
          <div
            ref={scrollRef}
            onScroll={checkScroll}
            className="flex gap-5 overflow-x-auto scrollbar-hide snap-x snap-mandatory pb-4"
          >
            {dashboards.map((dash, index) => (
              <motion.div
                key={dash.title}
                initial={{ opacity: 0, y: 40 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                className="snap-start flex-shrink-0 w-[320px] md:w-[400px] lg:w-[460px] rounded-2xl overflow-hidden relative group cursor-pointer"
                style={{ minHeight: '320px' }}
              >
                {/* Image */}
                <div className="absolute inset-0">
                  <img
                    src={dash.image}
                    alt={dash.title}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                </div>

                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-transparent" />

                {/* Status badge */}
                <div className="absolute top-4 right-4 z-20">
                  <span
                    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] tracking-widest uppercase font-semibold border backdrop-blur-sm ${
                      dash.status === 'CANLI'
                        ? 'bg-emerald-500/10 border-emerald-400/25 text-emerald-400'
                        : dash.status === 'KESTİRİMCİ'
                        ? 'bg-cyan-500/10 border-cyan-400/25 text-cyan-400'
                        : 'bg-amber-500/10 border-amber-400/25 text-amber-400'
                    }`}
                  >
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        dash.status === 'CANLI'
                          ? 'bg-emerald-400 animate-pulse'
                          : dash.status === 'KESTİRİMCİ'
                          ? 'bg-cyan-400 animate-pulse'
                          : 'bg-amber-400 animate-pulse'
                      }`}
                    />
                    {dash.status}
                  </span>
                </div>

                {/* Bottom info */}
                <div className="absolute bottom-0 left-0 right-0 p-5 md:p-6 z-20">
                  <h3 className="text-lg md:text-xl font-bold text-white">{dash.title}</h3>
                  <p className="mt-1.5 text-sm text-white/40 font-light leading-relaxed">
                    {dash.subtitle}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Scroll controls */}
          <div className="hidden md:flex items-center justify-between mt-8">
            <button
              onClick={() => scroll('left')}
              disabled={!canScrollLeft}
              className={`w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 ${
                canScrollLeft
                  ? 'border-white/15 text-white/60 hover:border-cyan-400/30 hover:text-cyan-400 cursor-pointer'
                  : 'border-white/5 text-white/15 cursor-default'
              }`}
            >
              <i className="ri-arrow-left-line text-lg" />
            </button>
            <button
              onClick={() => scroll('right')}
              disabled={!canScrollRight}
              className={`w-10 h-10 rounded-full border flex items-center justify-center transition-all duration-300 ${
                canScrollRight
                  ? 'border-white/15 text-white/60 hover:border-cyan-400/30 hover:text-cyan-400 cursor-pointer'
                  : 'border-white/5 text-white/15 cursor-default'
              }`}
            >
              <i className="ri-arrow-right-line text-lg" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
