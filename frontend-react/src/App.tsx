import { useHealth } from "./api";
import Nav from "./components/Nav";
import Hero from "./components/Hero";
import HowItWorks from "./components/HowItWorks";
import Architecture from "./components/Architecture";
import Footer from "./components/Footer";

export default function App() {
  const health = useHealth();
  return (
    <div className="min-h-screen bg-bg">
      <Nav health={health} />
      <Hero />
      <HowItWorks />
      <Architecture />
      <Footer />
    </div>
  );
}
