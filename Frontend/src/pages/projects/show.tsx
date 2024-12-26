import { Stack, Typography, Button } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useShow, useList } from "@refinedev/core";
import { Show, TextFieldComponent as TextField } from "@refinedev/mui";
import { Download as DownloadIcon, Add as AddIcon } from "@mui/icons-material";
import axios from "axios";
import { useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField as MuiTextField } from "@mui/material";

export const ProjectShow = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const { queryResult } = useShow({});
  const { data, isLoading } = queryResult;
  const record = data?.data;

  // State for modal
  const [open, setOpen] = useState(false);
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch secrets for this project
  const { data: secretsData, isLoading: secretsIsLoading, refetch } = useList({
    resource: "secrets",
    filters: [
      {
        field: "project_id",
        operator: "eq",
        value: record?.id,
      },
      {
        field: "secret_type_id",
        operator: "eq",
        value: 1, // RSA type
      },
    ],
  });

  const handleCreateRSA = async () => {
    try {
      setIsSubmitting(true);
      await axios.post(`${apiUrl}/secrets`, {
        description: description,
        created_by: "anonymous", // You might want to get this from your auth context
        project_id: record?.id,
        secret_type_id: 1,
        key_size: 2048
      });
      
      setOpen(false);
      setDescription("");
      // Refresh the secrets list
      refetch();
    } catch (error) {
      console.error('Failed to create RSA key:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDownload = async (secretId: number) => {
    try {
      const response = await axios.get(`${apiUrl}/secrets/${secretId}/download`, {
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `secret_${secretId}.zip`);
      
      // Append to html link element page
      document.body.appendChild(link);
      
      // Start download
      link.click();
      
      // Clean up and remove the link
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const columns = [
    {
      field: "id",
      headerName: "ID",
      type: "number",
      minWidth: 50,
    },
    {
      field: "description",
      headerName: "Description",
      flex: 1,
      minWidth: 200,
    },
    {
      field: "created_by",
      headerName: "Created By",
      minWidth: 150,
    },
    {
      field: "created_at",
      headerName: "Created At",
      minWidth: 180,
      renderCell: (params: any) => {
        return new Date(params.value).toLocaleString();
      },
    },
    {
      field: "actions",
      headerName: "Actions",
      minWidth: 200,
      renderCell: (params: any) => (
        <Button
          startIcon={<DownloadIcon />}
          onClick={() => handleDownload(params.row.id)}
          size="small"
        >
          Download
        </Button>
      ),
    },
  ] as GridColDef[];

  return (
    <Show isLoading={isLoading}>
      <Stack gap={1}>
        <Typography variant="body1" fontWeight="bold">
          Project Name
        </Typography>
        <TextField value={record?.project_name} />
        
        <Typography variant="body1" fontWeight="bold">
          Description
        </Typography>
        <TextField value={record?.description} />

        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 2, mb: 1 }}>
          <Typography variant="h6">
            RSA Keys
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
          >
            Generate New RSA Key
          </Button>
        </Stack>
        
        <DataGrid
          rows={secretsData?.data || []}
          columns={columns}
          loading={secretsIsLoading}
          pageSizeOptions={[5, 10, 25]}
          initialState={{
            pagination: {
              paginationModel: { pageSize: 5 },
            },
          }}
          sx={{
            "& .MuiDataGrid-cell:hover": {
              cursor: "pointer",
            },
          }}
        />

        {/* Modal for creating new RSA key */}
        <Dialog open={open} onClose={() => setOpen(false)}>
          <DialogTitle>Generate New RSA Key</DialogTitle>
          <DialogContent>
            <MuiTextField
              autoFocus
              margin="dense"
              label="Description"
              type="text"
              fullWidth
              variant="outlined"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleCreateRSA} 
              disabled={!description || isSubmitting}
              variant="contained"
            >
              Generate
            </Button>
          </DialogActions>
        </Dialog>
      </Stack>
    </Show>
  );
}; 