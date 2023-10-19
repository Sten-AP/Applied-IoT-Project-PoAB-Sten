/* eslint-disable react/prop-types */
import { MaterialReactTable } from "material-react-table";
import { useMemo, useState } from "react";
import { Button } from "@mui/material";

export function Bakenlijst({ bakens, statusVeranderen }) {
  const [buttonState, setButtonState] = useState(true);
  const columns = useMemo(
    () => [
      {
        accessorKey: "id",
        header: "Baken id",
        size: 150,
      },
      {
        accessorKey: "autoset",
        header: "Automatisch",
        size: 20,
      },
      {
        accessorKey: "status",
        header: "Verwachte status",
        size: 20,
      },
      {
        accessorKey: "lichtsterkte",
        header: "Lichtsterkte",
        size: 150,
      },
      {
        accessorKey: "luchtdruk",
        header: "Luchtdruk",
        size: 150,
      },
      {
        accessorKey: "temperatuur",
        header: "Temperatuur",
        size: 150,
      },
      {
        accessorKey: "latitude",
        header: "Latitude",
        size: 150,
      },
      {
        accessorKey: "longitude",
        header: "Longitude",
        size: 150,
      },
    ],
    []
  );

  return (
    <>
      <MaterialReactTable
        columns={columns}
        data={bakens}
        enableRowSelection
        positionToolbarAlertBanner="bottom"
        renderTopToolbarCustomActions={({ table }) => {
          setButtonState(true);
          if (table.getSelectedRowModel().flatRows.length > 0) {
            setButtonState(false)
          }

          const aanzetten = () => {
            table.getSelectedRowModel().flatRows.map((row) => {
              var param = "status";
              statusVeranderen(row.getValue("id"), param, 1);
              console.log(row.getValue("id") + " aangezet");
            });
          };

          const uitzetten = () => {
            table.getSelectedRowModel().flatRows.map((row) => {
              var param = "status";
              statusVeranderen(row.getValue("id"), param, 0);
              console.log(row.getValue("id") + " uitgezet");
            });
          };

          const automatisch = () => {
            table.getSelectedRowModel().flatRows.map((row) => {
              var param = "autoset";
              if (row.getValue("autoset") === 0) {
                statusVeranderen(row.getValue("id"), param, 1);
              } else {
                statusVeranderen(row.getValue("id"), param, 0);
              }
              console.log(row.getValue("id") + " automatisch");
            });
          };

          return (
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Button color="success" disabled={buttonState} onClick={aanzetten} variant="contained">
                aan
              </Button>
              <Button color="error" disabled={buttonState} onClick={uitzetten} variant="contained">
                uit
              </Button>
              <Button color="info" disabled={buttonState} onClick={automatisch} variant="contained">
                auto
              </Button>
            </div>
          );
        }}
      />
    </>
  );
}
