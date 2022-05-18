# Created by tonurmi at 12.5.2022
@file @ida @distribution
Feature: IDA File metadata
  User is able to upload files to the IDA-service, freeze them, and once frozen, select frozen files for inclusion in a
  dataset in the Qvain-service.

  """Other User Stories
  # When frozen by the user, IDA is able to publish the metadata for multiple frozen files with single API-call.
  Metax will save the frozen file-metadata, including name, size, relative project path, checksum, format, frozen
  timestamp, modification timestamp, creation timestamp, deletion timestamp, file-storage, internal identifier, and
  project identifier(s).

  Directories in Metax which are automatically derived from the relative project paths in the published frozen file
  metadata, and utilized within Metax and Qvain for convenience, but directory identifiers in Metax do not identify
  immutable file sets and do not have any meaning in the IDA-service.

  # Deprecating files
  User is able to unfreeze or delete frozen files in the IDA-service.

  # When unfrozen or deleted by the user, IDA is able to update the metadata for multiple frozen files with single
  API-call. Metax will update the frozen file-metadata, marking each file as deleted, and recording the deletion
  timestamp.

  If any unfrozen or deleted files are included in a dataset, Metax will mark that dataset as deprecated.

  IDA is able to query Metax to determine if any datasets will be deprecated if one or more frozen files are either
  unfrozen or deleted, so the user can be warned accordingly before taking any action.

  # Purging file metadata for projects
  # When a project is permanently deleted from the IDA-service, IDA is able to purge all frozen file metadata from Metax
  which is associated with that specific project. Metax will update the frozen file-metadata for every file associated
  with the deleted project, marking each file as deleted, and recording the deletion timestamp.

  User Stories retrieved 2022-05-17
  """

  Background:
    Given IDA has its own DataCatalog
    And IDA has its own DataStorage

  Scenario: IDA User freezes files
    When User freezes new files in IDA
    Then new Distribution is saved to database
    And Files are saved as part of Distribution
    And Distribution will have an IDA project identifier
    And Files and Distribution will have an freezing date
    And Distribution will have IDA as DataStorage

  Scenario: IDA user unfreezes files
    When User unfreezes file in IDA
    Then The file is marked as deleted
    Then Any Dataset with the file is marked as deprecated
