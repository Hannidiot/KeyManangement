import { Stack, Typography, Button } from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { useShow, useList } from "@refinedev/core";
import { Show, TextFieldComponent as TextField } from "@refinedev/mui";
import { Download as DownloadIcon } from "@mui/icons-material";
import axios from "axios";

export const ProjectShow = () => {
  const { queryResult } = useShow({});
  const { data, isLoading } = queryResult;
  const record = data?.data;

  // Fetch secrets for this project
  const { data: secretsData, isLoading: secretsIsLoading } = useList({
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

  const handleDownload = async (secretId: number) => {
    try {
      const response = await axios.get(`/api/secrets/${secretId}/download`, {
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
      minWidth: 100,
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

        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
          RSA Keys
        </Typography>
        
        <DataGrid
          rows={secretsData?.data || []}
          columns={columns}
          loading={secretsIsLoading}
          autoHeight
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
      </Stack>
    </Show>
  );
}; 