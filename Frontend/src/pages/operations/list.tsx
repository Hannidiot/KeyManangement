import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { List, useDataGrid } from "@refinedev/mui";
import React, { useState } from "react";
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  Typography,
  Tooltip,
  Box
} from "@mui/material";

interface DetailsDialogProps {
  open: boolean;
  details: string;
  onClose: () => void;
}

const DetailsDialog: React.FC<DetailsDialogProps> = ({ open, details, onClose }) => (
  <Dialog 
    open={open} 
    onClose={onClose}
    maxWidth="md"
    fullWidth
  >
    <DialogTitle>Operation Details</DialogTitle>
    <DialogContent>
      <Typography 
        sx={{ 
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          mt: 2 
        }}
      >
        {details}
      </Typography>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose}>Close</Button>
    </DialogActions>
  </Dialog>
);

export const OperationList = () => {
  const { dataGridProps } = useDataGrid({});
  const [selectedDetails, setSelectedDetails] = useState<string | null>(null);

  const columns = React.useMemo<GridColDef[]>(
    () => [
      {
        field: "id",
        headerName: "ID",
        type: "number",
        minWidth: 50,
        align: "left",
        headerAlign: "left",
      },
      {
        field: "username",
        flex: 1,
        headerName: "Username",
        minWidth: 150,
      },
      {
        field: "operation",
        flex: 1,
        headerName: "Operation",
        minWidth: 150,
      },
      {
        field: "timestamp",
        flex: 1,
        headerName: "Timestamp",
        minWidth: 200,
        renderCell: (params) => {
          return new Date(params.value).toLocaleString();
        },
      },
      {
        field: "details",
        flex: 2,
        headerName: "Details",
        minWidth: 300,
        renderCell: (params) => {
          const details = params.value as string;
          return (
            <Tooltip title="Click to view full details">
              <Box
                sx={{
                  cursor: 'pointer',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  width: '100%',
                  '&:hover': {
                    textDecoration: 'underline',
                  }
                }}
                onClick={() => setSelectedDetails(details)}
              >
                {details}
              </Box>
            </Tooltip>
          );
        },
      },
    ],
    []
  );

  return (
    <>
      <List>
        <DataGrid 
          {...dataGridProps} 
          columns={columns}
          autoHeight
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: {
              paginationModel: { pageSize: 10 },
            },
          }}
          sx={{
            '& .MuiDataGrid-cell': {
              cursor: 'pointer',
            },
          }}
        />
      </List>

      <DetailsDialog
        open={Boolean(selectedDetails)}
        details={selectedDetails || ''}
        onClose={() => setSelectedDetails(null)}
      />
    </>
  );
}; 