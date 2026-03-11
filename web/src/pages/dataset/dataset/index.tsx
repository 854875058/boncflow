import { BulkOperateBar } from '@/components/bulk-operate-bar';
import { FileUploadDialog } from '@/components/file-upload-dialog';
import ListFilterBar from '@/components/list-filter-bar';
import { RenameDialog } from '@/components/rename-dialog';
import { Button, ButtonLoading } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Modal } from '@/components/ui/modal/modal';
import { useRowSelection } from '@/hooks/logic-hooks/use-row-selection';
import { useFetchDocumentList } from '@/hooks/use-document-request';
import { useFetchKnowledgeBaseConfiguration } from '@/hooks/use-knowledge-request';
import { Pen, Upload, WandSparkles } from 'lucide-react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
  MetadataType,
  useManageMetadata,
} from '../components/metedata/hooks/use-manage-modal';
import { ManageMetadataModal } from '../components/metedata/manage-modal';
import { DatasetTable } from './dataset-table';
import Generate from './generate-button/generate';
import { useDatasetGenerate } from './generate-button/hook';
import { ReparseDialog } from './reparse-dialog';
import { useBulkOperateDataset } from './use-bulk-operate-dataset';
import { useCreateEmptyDocument } from './use-create-empty-document';
import { useSelectDatasetFilters } from './use-select-filters';
import { useHandleUploadDocument } from './use-upload-document';

export default function Dataset() {
  const { t } = useTranslation();
  const {
    documentUploadVisible,
    hideDocumentUploadModal,
    showDocumentUploadModal,
    onDocumentUploadOk,
    documentUploadLoading,
  } = useHandleUploadDocument();

  const {
    searchString,
    documents,
    pagination,
    handleInputChange,
    setPagination,
    filterValue,
    handleFilterSubmit,
    loading,
  } = useFetchDocumentList();

  const refreshCount = useMemo(() => {
    return documents.findIndex((doc) => doc.run === '1') + documents.length;
  }, [documents]);

  const { data: dataSetData } = useFetchKnowledgeBaseConfiguration({
    refreshCount,
  });
  const { rebuildMultimodal, rebuildingMultimodal } = useDatasetGenerate();
  const { filters, onOpenChange, filterGroup } = useSelectDatasetFilters();

  const {
    createLoading,
    onCreateOk,
    createVisible,
    hideCreateModal,
    showCreateModal,
  } = useCreateEmptyDocument();

  const {
    manageMetadataVisible,
    showManageMetadataModal,
    hideManageMetadataModal,
    tableData,
    config: metadataConfig,
  } = useManageMetadata();

  const { rowSelection, rowSelectionIsEmpty, setRowSelection, selectedCount } =
    useRowSelection();

  const {
    chunkNum,
    list,
    visible: reparseDialogVisible,
    hideModal: hideReparseDialogModal,
    handleRunClick: handleOperationIconClick,
  } = useBulkOperateDataset({
    documents,
    rowSelection,
    setRowSelection,
  });

  const handleRebuildMultimodal = () => {
    Modal.show({
      visible: true,
      title: '重建多模态索引',
      children: (
        <div className="space-y-3 text-sm text-text-secondary">
          <p>将重新解析当前知识库中的所有非空文件，并重建图片块的多模态融合向量。</p>
          <p>原有 chunk 会被删除后重新生成，过程可能持续较长时间。</p>
          <p>如果当前知识库还有文件正在解析，请等待完成后再执行。</p>
        </div>
      ),
      onCancel: () => Modal.destroy(),
      footer: (
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => Modal.destroy()}>
            {t('common.cancel')}
          </Button>
          <ButtonLoading
            loading={rebuildingMultimodal}
            onClick={async () => {
              const ret = await rebuildMultimodal();
              if (ret?.code === 0) {
                Modal.destroy();
              }
            }}
          >
            开始重建
          </ButtonLoading>
        </div>
      ),
    });
  };
  return (
    <>
      <div className="absolute top-4 right-5 flex items-center gap-2">
        <Button
          variant="transparent"
          disabled={!(dataSetData?.doc_num > 0)}
          onClick={handleRebuildMultimodal}
        >
          <WandSparkles className="mr-2 size-4" />
          重建多模态索引
        </Button>
        <Generate disabled={!(dataSetData.chunk_num > 0)} />
      </div>
      <section className="p-5 min-w-[880px]">
        <ListFilterBar
          title="Dataset"
          onSearchChange={handleInputChange}
          searchString={searchString}
          value={filterValue}
          filterGroup={filterGroup}
          onChange={handleFilterSubmit}
          onOpenChange={onOpenChange}
          filters={filters}
          leftPanel={
            <div className="items-start">
              <div className="pb-1">{t('knowledgeDetails.subbarFiles')}</div>
              <div className="text-text-secondary text-sm">
                {t('knowledgeDetails.datasetDescription')}
              </div>
            </div>
          }
          preChildren={
            <Button
              variant={'ghost'}
              className="border border-border-button"
              onClick={() =>
                showManageMetadataModal({
                  type: MetadataType.Manage,
                  isCanAdd: false,
                  isEditField: true,
                  title: (
                    <div className="flex flex-col gap-2">
                      <div className="text-base font-normal">
                        {t('knowledgeDetails.metadata.manageMetadata')}
                      </div>
                      <div className="text-sm text-text-secondary">
                        {t(
                          'knowledgeDetails.metadata.manageMetadataForDataset',
                        )}
                      </div>
                    </div>
                  ),
                })
              }
            >
              <div className="flex gap-1 items-center">
                <Pen size={14} />
                {t('knowledgeDetails.metadata.metadata')}
              </div>
            </Button>
          }
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size={'sm'}>
                <Upload />
                {t('knowledgeDetails.addFile')}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
              <DropdownMenuItem onClick={showDocumentUploadModal}>
                {t('fileManager.uploadFile')}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={showCreateModal}>
                {t('knowledgeDetails.emptyFiles')}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </ListFilterBar>
        {rowSelectionIsEmpty || (
          <BulkOperateBar list={list} count={selectedCount}></BulkOperateBar>
        )}
        <DatasetTable
          documents={documents}
          pagination={pagination}
          setPagination={setPagination}
          rowSelection={rowSelection}
          setRowSelection={setRowSelection}
          showManageMetadataModal={showManageMetadataModal}
          loading={loading}
        ></DatasetTable>
        {documentUploadVisible && (
          <FileUploadDialog
            hideModal={hideDocumentUploadModal}
            onOk={onDocumentUploadOk}
            loading={documentUploadLoading}
            showParseOnCreation
          ></FileUploadDialog>
        )}
        {createVisible && (
          <RenameDialog
            hideModal={hideCreateModal}
            onOk={onCreateOk}
            loading={createLoading}
            title={'File Name'}
          ></RenameDialog>
        )}
        {manageMetadataVisible && (
          <ManageMetadataModal
            title={
              metadataConfig.title || (
                <div className="flex flex-col gap-2">
                  <div className="text-base font-normal">
                    {t('knowledgeDetails.metadata.manageMetadata')}
                  </div>
                  <div className="text-sm text-text-secondary">
                    {t('knowledgeDetails.metadata.manageMetadataForDataset')}
                  </div>
                </div>
              )
            }
            visible={manageMetadataVisible}
            hideModal={hideManageMetadataModal}
            // selectedRowKeys={selectedRowKeys}
            tableData={tableData}
            isCanAdd={metadataConfig.isCanAdd}
            isEditField={metadataConfig.isEditField}
            isDeleteSingleValue={metadataConfig.isDeleteSingleValue}
            type={metadataConfig.type}
            otherData={metadataConfig.record}
          />
        )}
        {reparseDialogVisible && (
          <ReparseDialog
            // hidden={isZeroChunk || isRunning}
            hidden={false}
            handleOperationIconClick={handleOperationIconClick}
            chunk_num={chunkNum}
            visible={reparseDialogVisible}
            hideModal={hideReparseDialogModal}
          ></ReparseDialog>
        )}
      </section>
    </>
  );
}
