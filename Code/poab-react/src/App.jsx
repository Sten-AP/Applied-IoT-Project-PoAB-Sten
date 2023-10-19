/* eslint-disable no-unused-vars */
import axios from "axios";
import React, { useEffect, useState } from "react";
import { Header } from "./Header";
import { Bakenlijst } from "./Bakenlijst";

const api = axios.create({
  baseURL: "http://localhost:7000",
});

export default function App() {
  const [bakens, setBakens] = useState([]);

  const opvragenBakens = async () => {
    const response = await api.get("/baken/");
    setBakens(response.data);
  };

  const statusVeranderen = async (id, param, value) => {
    const response = await api.post(`/baken/${id}/${param}/?status=${value}`);
    console.log(response.data);
    opvragenBakens();
  };

  useEffect(() => {
    opvragenBakens();
  }, []);

  return (
    <>
      <Header />
      <Bakenlijst bakens={bakens} statusVeranderen={statusVeranderen} />
      <br />
      <div className="iframes">
        <iframe src="http://poab.iot-ap.be:3000/d-solo/f124257f-031c-4658-8f19-3fba329a3033/poab?orgId=1&panelId=3&refresh=5s&theme=light" width="900" height="400" frameborder="0"></iframe>
        <iframe src="http://poab.iot-ap.be:3000/d-solo/f124257f-031c-4658-8f19-3fba329a3033/poab?orgId=1&theme=light&panelId=1&refresh=5s" width="900" height="400" frameborder="0"></iframe>
      </div>
      <br />
      <div className="iframes">
        <iframe src="http://poab.iot-ap.be:3000/d-solo/f124257f-031c-4658-8f19-3fba329a3033/poab?orgId=1&panelId=4&refresh=5s&theme=light" width="900" height="400" frameborder="0"></iframe>
        <iframe src="http://poab.iot-ap.be:3000/d-solo/f124257f-031c-4658-8f19-3fba329a3033/poab?orgId=1&theme=light&panelId=5&refresh=5s" width="900" height="400" frameborder="0"></iframe>
      </div>
    </>
  );
}
