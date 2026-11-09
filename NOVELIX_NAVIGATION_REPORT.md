# NOVELIX 8.0 — Navigation Architecture Report

**Generated:** 2026-11-09  
**Controller:** `NavigationController` (`scripts/generate_4.py`, lines 2125–2215)  
**Primary Routes:** Home, Explore, Library, Publish, Profile, Drive, Settings, Reader

---

## 1. Unified Navigation Controller Architecture

The NOVELIX application navigation is centralized under `NavigationController`.

```
                        ┌────────────────────────┐
                        │  NavigationController  │
                        └───────────┬────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
┌───▼───────────────┐      ┌────────▼──────────────┐      ┌─────────▼───────────────┐
│     init()        │      │    navigate(pageId)   │      │   handleBackButton(e)   │
│ - Reset all modals│      │ - Push history stack  │      │ - Reader Modal close    │
│ - Clear PDF state │      │ - switchPage(pageId)  │      │ - Detail Modal close    │
│ - Enforce 'home'  │      │ - Viewport scroll top │      │ - Secondary -> Home     │
└───────────────────┘      └───────────────────────┘      │ - Home double tap exit  │
                                                          └─────────────────────────┘
```

---

## 2. Startup State Enforcement

On every app launch or resume:
1. All `.modal-fullscreen` and `.modal-sheet` elements have the `.open` class forcibly removed.
2. Body scroll lock is reset: `document.body.style.overflow = ''; document.body.style.position = '';`.
3. Reader rendering state is cleared: `APP_STATE.pdfDocument = null`, `APP_STATE.pdfIsRendering = false`.
4. Obsolete render tasks are aborted: `if (APP_STATE._currentRenderTask) APP_STATE._currentRenderTask.cancel()`.
5. The view router activates `page-home` and highlights `nav-home`.

This guarantees that NOVELIX **never opens into a reader or detail modal upon launching**.

---

## 3. Android Hardware Back Button Hierarchy

The back button event listener is wired directly to `NavigationController.handleBackButton(e)`:

| Priority | Active State | Back Action Taken |
|---|---|---|
| **Level 1** | Reader Modal is open (`#readerModal.open`) | Closes reader, restores body scroll, cancels active render task, re-opens Book Detail modal |
| **Level 2** | Book Detail Modal is open (`#bookDetailModal.open`) | Closes Book Detail modal, restores focus to active catalog |
| **Level 3** | Any Secondary Modal is open (`authModal`, `adminDashboardModal`, etc.) | Closes open modal |
| **Level 4** | Developer Terminal is open (`#devTerminal.open`) | Closes developer terminal |
| **Level 5** | Secondary Navigation Tab active (`explore`, `library`, `publish`, `profile`) | Smoothly switches back to `home` |
| **Level 6** | Already on `home` tab | Requires double-tap within 2.0 seconds to exit application (`Capacitor.Plugins.App.exitApp()`) with feedback toast |
