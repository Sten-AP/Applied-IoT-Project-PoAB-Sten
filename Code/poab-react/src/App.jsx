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

 //  const opvragenBakens = async () => {
 // const response = await api.get("/baken/");
 // response = await fetch("/baken/");
 // setBakens(response.data);
 //  };

 const opvragenBakens = async () => {
  fetch("/baken/")
   .then((response) => {
    return response.json();
   })
   .then((data) => setBakens(data));
 };

 const statusVeranderen = async (id, param, value) => {
  const response = await api.post(`/baken/${id}/${param}/?status=${value}`);
  console.log(response.data);
  opvragenBakens();
 };

 useEffect(() => {
  opvragenBakens();
  const socket = new WebSocket("ws://example.com"); // Vervang dit met je eigen WebSocket-server URL

  // Eventlisteners voor WebSocket-gebeurtenissen
  socket.addEventListener("open", (event) => {
   console.log("WebSocket-verbinding geopend:", event);
  });

  socket.addEventListener("message", (event) => {
   console.log("Ontvangen bericht:", event.data);
  });

  socket.addEventListener("close", (event) => {
   console.log("WebSocket-verbinding gesloten:", event);
  });

  // Schoonmaak bij het demonteren van de component
  return () => {
   socket.close();
  };
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
