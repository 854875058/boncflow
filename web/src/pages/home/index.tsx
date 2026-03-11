import { Applications } from './applications';
import { NextBanner } from './banner';
import { Datasets } from './datasets';

const Home = () => {
  return (
    <section className="bg-bg-title h-full">
      {/* <NextBanner></NextBanner> */}
      <section className="px-10 py-10 overflow-auto h-full bg-bg-title">
        <Datasets></Datasets>
        <Applications></Applications>
      </section>
    </section>
  );
};

export default Home;
