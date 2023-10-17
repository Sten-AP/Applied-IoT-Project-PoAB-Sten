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
  };

  useEffect(() => {
    opvragenBakens();
  }, []);

  return (
    <>
      <Header />
      <Bakenlijst bakens={bakens} statusVeranderen={statusVeranderen} opvragenBakens={opvragenBakens} />
    </>
  );
}
